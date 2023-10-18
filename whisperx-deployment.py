import os
import whisperx
import json
import gc
import logging
import httpx
import huggingface_hub
import requests
import numpy as np
from time import time
from starlette.requests import Request
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from typing import Dict
from torch import cuda
from services.s3_service import *
from services.audio_service import *
from ray.serve.handle import DeploymentHandle
from ray import serve
from subprocess import CalledProcessError
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ray.serve")

##########
# from dotenv import load_dotenv
# load_dotenv(dotenv_path='/home/team983/secret/.env')
##########

app = FastAPI()

@serve.deployment
@serve.ingress(app)
class APIIngress:
    def __init__(self, live_handle: DeploymentHandle, full_handle: DeploymentHandle) -> None:
        self.live_handle=live_handle.options(use_new_handle_api=True)
        self.full_handle=full_handle.options(use_new_handle_api=True)
        self.LIVE_UPLOAD_DIR = 'live'
        self.FULL_UPLOAD_DIR = 'full'
        os.makedirs(self.LIVE_UPLOAD_DIR, exist_ok=True)
        os.makedirs(self.FULL_UPLOAD_DIR, exist_ok=True)


    @app.websocket("/live")
    async def live_stt(self, ws: WebSocket) -> None:
        await ws.accept()
        try:
            while True:
                audio_data = await ws.receive_bytes()
                if audio_data:
                    request_time = time()
                    file_name = os.path.join(os.getcwd(), self.LIVE_UPLOAD_DIR, f'audio_file_{request_time}.bin')
                    with open(file_name, "wb") as f:
                        f.write(audio_data)
                    response = self.live_handle.transcribe_audio.remote(file_name)
                    result = await response
                    await ws.send_json(result)
        except WebSocketDisconnect:
            ws.close()
            print("Client disconnected.")
    

    @app.post("/asr/{note_id}", status_code=202)
    async def full_stt(self, note_id:str, request: Request) -> Dict:
        request = await request.json()
        note_id = int(note_id)
        if type(request) != dict:
            request = json.loads(request)
        og_filename = request.get("filename")
        print(f'Received file name: {og_filename}')
        logger.info(f'Received file name: {og_filename}')
        og_filepath = os.path.join(os.getcwd(), self.FULL_UPLOAD_DIR, og_filename)
        download_file_from_s3(og_filepath)
        try:
            converted_filepath = convert_to_m4a(og_filepath)
            converted_filename = os.path.basename(converted_filepath)
            if os.path.exists(og_filepath):
                os.remove(og_filepath)
            duration = get_audio_duration(converted_filepath)

            delete_file_from_s3(og_filename)
            upload_file_to_s3(converted_filepath)
            
            s3ObjectUrl = get_s3_object_url(converted_filename)
            logger.info('Original: %s, Converted to m4a at: %s, Duration: %f', og_filepath, converted_filepath, duration)

            model_type = request.get('category')
            model_id = await self.full_handle.get_model_id.options(multiplexed_model_id=model_type).remote()
            self.full_handle.get_model.remote(model_id)

            audio = whisperx.load_audio(converted_filepath)
            self.full_handle.transcribe_audio.remote(note_id, audio)

            if os.path.exists(converted_filepath):
                os.remove(converted_filepath)
            
            return {
                "noteId": note_id,
                "filename": converted_filename,
                "duration": duration,
                "s3ObjectUrl": s3ObjectUrl,
                "status": "PROCESSING"
            }
        except CalledProcessError as e:
            logger.error(f"Error ffmpeg CalledProcessError {note_id} {og_filename}. Error: {str(e)}")
            return self.preprocessing_error(note_id, og_filename)
        except FileNotFoundError as e:
            logger.error(f"Error FileNotFoundError {note_id} {og_filename}. Error: {str(e)}")
            return self.preprocessing_error(note_id, og_filename)
        except Exception as e:
            logger.error(f"Error occurred! {note_id} {og_filename}. Error: {str(e)}")
            return self.preprocessing_error(note_id, og_filename)


    def preprocessing_error(self, note_id: int, file_name: str):
        if os.path.exists(file_name):
            os.remove(file_name)

        converted_filepath = os.path.splitext(file_name)[0] + ".m4a"
        if os.path.exists(converted_filepath):
            os.remove(converted_filepath)

        return {
            "noteId": note_id,
            "filename": file_name,
            "duration": None,
            "s3ObjectUrl": None,
            "status": "PREPROCESSING_ERROR"
        }


    @app.get('/healthy')
    def healthy(self):
        logger.info('hello')
        return {"result" : ["healthy"]}
    

@serve.deployment
class LiveSTT:
    def __init__(self):
        device = 'cuda' if cuda.is_available() else 'cpu'
        compute_type = 'int8'
        self.asr_model = whisperx.load_model('small', device, language='ko', compute_type=compute_type)


    def transcribe_audio(self, file_name:str):
        logger.info(f"Start live transcribing: {file_name}")
        start_time = time()
        batch_size = 1 
        try:
            audio = whisperx.load_audio(file_name)
            result = self.asr_model.transcribe(audio, batch_size=batch_size)
            result["status"] = "SUCCESS"           
            end_time = time()
            logger.info(f"Total time taken: {end_time - start_time}")

        except Exception as e:
            logger.error(f"Error processing {file_name}. Error: {str(e)}")
            if str(e) == "0":
                result = {"message": "No active speech found in audio", "status":"ERROR"}
    
            else:
                # Inform the server about the remaining error
                result = {"message": str(e), "status":"ERROR"}

        finally:
            if os.path.exists(file_name):
                os.remove(file_name)
            gc.collect()
            cuda.empty_cache()
            return result


@serve.deployment
class FullSTT:
    def __init__(self):
        self._MODELS = {
                    "GENERAL": "guillaumekln/faster-whisper-large-v2",
                    "IT": "yongchanskii/whisperx-for-developers"
        }

        allow_patterns = [
            "config.json",
            "model.bin",
            "tokenizer.json",
            "vocabulary.*",
        ]

        kwargs = {
                "local_files_only": False,
                "allow_patterns": allow_patterns,
        }
        for model_name in self._MODELS:
            try:
                huggingface_hub.snapshot_download(self._MODELS.get(model_name), **kwargs)
            except (
                huggingface_hub.utils.HfHubHTTPError,
                requests.exceptions.ConnectionError,
            ) as exception:
                kwargs["local_files_only"] = True
                huggingface_hub.snapshot_download(self._MODELS.get(model_name), **kwargs)

        self.device = "cuda" if cuda.is_available() else "cpu"
        self.diarize_model = whisperx.DiarizationPipeline(use_auth_token=os.getenv("HF_API_KEY"), device=self.device)
      

    @serve.multiplexed(max_num_models_per_replica=1)
    async def get_model(self, model_id):
        logger.info(f"Loading model {model_id}")
        compute_type = "int8" # change to "int8" if low on GPU mem (may reduce accuracy)
        self.asr_model = whisperx.load_model(self._MODELS.get(model_id), self.device, language='ko', compute_type=compute_type)


    def get_model_id(self):
        return serve.get_multiplexed_model_id()
    
    def transcribe_audio(self, note_id:int, audio:np.ndarray):
        logger.info(f"Start transcribing note id: {note_id}")
        start_time = time()
        batch_size = 2 # reduce if low on GPU mem
        try:
            # 1. Transcribe with faster-whisper (batched)
            result = self.asr_model.transcribe(audio, batch_size=batch_size)
            transcription_end_time = time()
            logger.info(f'Total time taken for transcription: {transcription_end_time-start_time}')

            # 2. Assign speaker labels
            diarize_start_time = time()
            diarize_segments = self.diarize_model(audio)
            result = whisperx.assign_word_speakers(diarize_segments, result)
            diarize_end_time = time()
            logger.info(f'Total time taken for diarization: {diarize_end_time-diarize_start_time}')
            
            end_time = time()
            logger.info(f"Total time taken: {end_time - start_time}")
            result['noteId'] = note_id
            response = httpx.post(f"https://dev.synnote.com/api/v1/note/whisperx-asr-completed", json=result)

        except Exception as e:
            logger.error(f"Error processing {note_id}. Error: {str(e)}")
            if str(e) == "0":
                result = {"noteId": note_id, "message": "No active speech found in audio", "status":"NO_SPEECH_ERROR"}
                response = httpx.post(f"https://dev.synnote.com/api/v1/note/asr-error", json=result)
    
            else:
                # Inform the server about the remaining error
                result = {"noteId": note_id, "message": str(e), "status":"ERROR"}
                response = httpx.post(f"https://dev.synnote.com/api/v1/note/asr-error", json=result)
                
        finally:
            gc.collect()
            cuda.empty_cache()
            logger.info(f'NoteId:{note_id} response: {response}')

live_stt = LiveSTT.bind()
full_stt = FullSTT.bind()
entrypoint = APIIngress.bind(live_stt, full_stt)
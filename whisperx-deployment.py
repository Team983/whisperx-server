import os
import whisperx
import json
import gc
import logging
import httpx
import huggingface_hub
import requests
from time import time
from starlette.requests import Request
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from typing import Dict
from torch import cuda
from services.s3_service import download_file_from_s3
from ray.serve.handle import DeploymentHandle
from ray import serve, get

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ray.serve")

app = FastAPI()

@serve.deployment
@serve.ingress(app)
class APIIngress:
    def __init__(self, live_handle: DeploymentHandle, full_handle: DeploymentHandle) -> None:
        self.live_handle=live_handle
        self.full_handle=full_handle
        self.LIVE_UPLOAD_DIR = 'live'
        os.makedirs(self.LIVE_UPLOAD_DIR, exist_ok=True)

    # JSON 형식으로 데이터를 받는 경우
    # @app.websocket("/live")
    # async def live_stt(self, ws: WebSocket) -> None:
    #     await ws.accept()
    #     try:
    #         while True:
    #             data = await ws.receive_json()
    #             user_id = data["userId"]
    #             audio_data = bytes(data["audioData"])
    #             if user_id and audio_data:
    #                 file_name = os.path.join(self.LIVE_UPLOAD_DIR, f'audio_file_{user_id}.bin')
    #                 with open(file_name, "wb") as f:
    #                     f.write(audio_data)
    #                 response = self.live_handle.transcribe_audio.remote(file_name)
    #                 result = await response
    #                 await ws.send_json(get(result))
    #     except WebSocketDisconnect:
    #         ws.close()
    #         print("Client disconnected.")

    @app.websocket("/live")
    async def live_stt(self, ws: WebSocket) -> None:
        await ws.accept()
        try:
            while True:
                audio_data = await ws.receive_bytes()
                if audio_data:
                    request_time = time()
                    file_name = os.path.join(self.LIVE_UPLOAD_DIR, f'audio_file_{request_time}.bin')
                    with open(file_name, "wb") as f:
                        f.write(audio_data)
                    response = self.live_handle.transcribe_audio.remote(file_name)
                    result = await response
                    await ws.send_json(get(result))
        except WebSocketDisconnect:
            ws.close()
            print("Client disconnected.")


    @app.post("/asr/{note_id}", status_code=202)
    async def full_stt(self, note_id:str, request: Request) -> Dict:
        request = await request.json()
        request = json.loads(request)
        file_name = request['file_name']
        model_id = serve.get_multiplexed_model_id()
        # download_file_from_s3(file_name)
        await self.full_handle.get_model.remote(model_id)
        self.full_handle.transcribe_audio.remote(note_id, file_name)
        return {"noteId": note_id, "fileName": file_name}

    @app.get('/healthy')
    def healthy(self):
        logger.info('hello')
        return {"result" : ["healthy"]}
    

@serve.deployment(ray_actor_options={"num_cpus":1, "num_gpus": 0.2})
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
            text = self.asr_model.transcribe(audio, batch_size=batch_size)           
            end_time = time()
            logger.info(f"Total time taken: {end_time - start_time}")
            result = {"result": text, "valid":True}

        except Exception as e:
            logger.error(f"Error processing {file_name}. Error: {str(e)}")
            if str(e) == "0":
                # Consider error caused by "No active speech found in audio" as a successful transcription
                # 수정필요
                result = {"result": "No active speech found in audio", "valid":False}
    
            else:
                # Inform the server about the remaining error
                result = {"result": str(e), "valid":False}
    
        finally:
            if os.path.exists(file_name):
                os.remove(file_name)
            gc.collect()
            cuda.empty_cache()
            return result


@serve.deployment(ray_actor_options={"num_cpus":1, "num_gpus": 0.2})
class FullSTT:

    def __init__(self):
        self._MODELS = {
                    "large-v2": "guillaumekln/faster-whisper-large-v2",
                    "software-development": "yongchanskii/whisperx-for-developers"
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


    def transcribe_audio(self, note_id:str, file_name:str):
        logger.info(f"Start transcribing note id: {note_id}")
        download_file_from_s3(file_name)
        start_time = time()
        batch_size = 2 # reduce if low on GPU mem
        file_path = os.path.join(os.getcwd(), file_name)
        try:
            audio = whisperx.load_audio(file_path)

            # 2. Transcribe with faster-whisper (batched)
            result = self.asr_model.transcribe(audio, batch_size=batch_size)
            transcription_end_time = time()
            logger.info(f'Total time taken for transcription: {transcription_end_time-start_time}')

            # 3. Assign speaker labels
            diarize_start_time = time()
            diarize_segments = self.diarize_model(audio)
            result = whisperx.assign_word_speakers(diarize_segments, result)
            diarize_end_time = time()
            logger.info(f'Total time taken for diarization: {diarize_end_time-diarize_start_time}')
            
            end_time = time()
            logger.info(f"Total time taken: {end_time - start_time}")
            data = {"noteId": note_id, "result": result, "valid": True}
            httpx.post(f"http://220.118.70.197:9000/asr-completed/{note_id}", json=data)

        except Exception as e:
            logger.error(f"Error processing {note_id} {file_name}. Error: {str(e)}")
            if str(e) == "0":
                # Consider error caused by "No active speech found in audio" as a successful transcription
                # 수정필요
                data = {"noteId": note_id, "result": "No active speech found in audio", "valid":False}
                httpx.post(f"http://220.118.70.197:9000/asr-completed/{note_id}", json=data)
    
            else:
                # Inform the server about the remaining error
                error_data = {"noteId": note_id, "message": str(e), "valid":False}
                httpx.post(f"http://220.118.70.197:9000/asr-error/{note_id}", json=error_data)
    
        finally:
            if os.path.exists(file_name):
                os.remove(file_name)
            gc.collect()
            cuda.empty_cache()

live_stt = LiveSTT.bind()
full_stt = FullSTT.bind()
entrypoint = APIIngress.bind(live_stt, full_stt)



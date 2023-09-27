import os
import whisperx
import json
import gc
import logging
import httpx
import threading
from torch import cuda
from time import time
from starlette.requests import Request
from fastapi import FastAPI
from typing import Dict
from ray import serve, remote, init
from dotenv import load_dotenv
from services.s3_service import download_file_from_s3
from starlette.background import BackgroundTasks
from ray.util.queue import Queue
from ray import serve
from ray.serve.handle import RayServeDeploymentHandle

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('ray.serve')

app = FastAPI()

init(dashboard_host='0.0.0.0')

@serve.deployment(num_replicas=1)
@serve.ingress(app)
class APIIngress:
    def __init__(self, handle: RayServeDeploymentHandle) -> None:
        self.handle=handle


    @app.post("/asr/{note_id}", status_code=202)
    async def stt(self, note_id:str, request: Request) -> Dict:
        request = await request.json()
        request = json.loads(request)
        file_name = request['file_name']
        # download_file_from_s3(file_name)
        self.handle.transcribe_audio.remote(note_id, file_name)
        return {"noteId": note_id, "fileName": file_name}


    @app.get('/healthy')
    def healthy(self):
        logger.info('hello')
        return {"result" : ["healthy"]}
    

@serve.deployment(
    ray_actor_options={"num_gpus": 0.2},
    autoscaling_config={
        "min_replicas": 0,
        "initial_replicas": 0,
        "max_replicas": 2,
        "target_num_ongoing_requests_per_replica": 2,   # number of requests being processed and waiting in the queue. 
        },
)
class WhisperxDeployment:

    def __init__(self, model_name:str='large-v2'):
        asr_model, diarize_model, device = self.set_whisperx(model_name)
        self.asr_model = asr_model
        self.diarize_model = diarize_model
        self.device = device


    def set_whisperx(self, model_name='large-v2'):
        if cuda.is_available():
            device_id = 0
            cuda.set_device(device_id)
            device = "cuda"
        else:
            device = 'cpu'

        compute_type = "int8" # change to "int8" if low on GPU mem (may reduce accuracy)
        asr_model = whisperx.load_model(model_name, device, language='ko', compute_type=compute_type)
        diarize_model = whisperx.DiarizationPipeline(use_auth_token=os.getenv("HF_API_KEY"), device=device)
        return asr_model, diarize_model, device


    def transcribe_audio(self, note_id:str , file_name:str):
        logger.info(f"Start transcribing node id: {note_id}")
        download_file_from_s3(file_name)
        start_time = time()
        batch_size = 2 # reduce if low on GPU mem
        file_path = os.path.join(os.getcwd(), file_name)
        try:
            audio = whisperx.load_audio(file_path)

            # 2. Transcribe with faster-whisper (batched)
            result = self.asr_model.transcribe(audio, batch_size=batch_size, num_workers=1)
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
            data = {"noteId": note_id, "result": result}
            httpx.post(f"http://127.0.0.1:8000/asr-completed/{note_id}", json=data)

        except Exception as e:
            logger.error(f"Error processing {note_id} {file_name}. Error: {str(e)}")

            if e == 0:
                # Consider error caused by "No active speech found in audio" as a successful transcription
                data = {"noteId": note_id, "result": result}
                httpx.post(f"http://127.0.0.1:8000/asr-completed/{note_id}", json=data)

            else:
                # Inform the server about the remaining error
                error_data = {"noteId": note_id, "message": str(e)}
                httpx.post(f"http://127.0.0.1:8000/asr-error/{note_id}", json=error_data)
    
        finally:
            if os.path.exists(file_name):
                os.remove(file_name)
            gc.collect()
            cuda.empty_cache()


entrypoint = APIIngress.bind(WhisperxDeployment.bind())


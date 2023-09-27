import os
import whisperx
import json
from time import time
from starlette.requests import Request
from fastapi import FastAPI
from typing import Dict
from ray import serve
from torch import cuda
from dotenv import load_dotenv
from services.s3_service import download_file_from_s3

load_dotenv()
app = FastAPI()
# 1: Define a Ray Serve application.
@serve.deployment(num_replicas=1, ray_actor_options={"num_cpus":3, "num_gpus": 0.2}, route_prefix="/")
@serve.ingress(app)
class WhisperxDeployment:

    def __init__(self, model_name='small'):
        asr_model, device = self.set_whisperx(model_name)
        self.asr_model = asr_model
        self.device = device
    
    
    @app.post("/asr/{note_id}")
    async def stt(self, note_id:str, request: Request) -> Dict:
        request = await request.json()
        request = json.loads(request)
        file_name = request['file_name']
        download_file_from_s3(file_name)
        result = self.transcribe_audio(file_name)
        return {"noteId": note_id, "result": result}
    

    @app.get('/healthy')
    def healthy(self):
        return {"result" : ["healthy"]}


    def set_whisperx(self, model_name='small'):
        device = "cuda" if cuda.is_available() else 'cpu'
        compute_type = "int8" # change to "int8" if low on GPU mem (may reduce accuracy)
        # 2. Transcribe with faster-whisper (batched)
        asr_model = whisperx.load_model(model_name, device, compute_type=compute_type)
        return asr_model, device


    def transcribe_audio(self, file_name: str):
        start_time = time()
        batch_size = 16 # reduce if low on GPU mem
        file_path = os.path.join(os.getcwd(), file_name)
        audio = whisperx.load_audio(file_path)
        result = self.asr_model.transcribe(audio, batch_size=batch_size)
        print('Finished transcribing')
        # delete model if low on GPU resources
        # import gc; gc.collect(); torch.cuda.empty_cache(); del model

        if os.path.exists(file_name):
            os.remove(file_name)
        end_time = time()
        'Start time:', start_time, 'End time:', end_time
        Total time taken: {end_time - start_time}
        logger.info(f"")
        # print(f"Total time taken: {end_time - start_time}")
        return result


whisperx_app = WhisperxDeployment.bind()
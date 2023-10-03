import requests
import json
import time

file_name = {"file_name":"2023-08-07T02:54:38.350820519_audio-756-yorkie.webm"}
# answer = requests.post("http://localhost:8000/asr/1", json=json.dumps(file_name), headers={"serve_multiplexed_model_id": "large-v2"})
# answer = requests.post("http://localhost:8000/asr/2", json=json.dumps(file_name), headers={"serve_multiplexed_model_id": "software-development"})
answer = requests.post("http://localhost:8081/asr/1", json=json.dumps(file_name), headers={"serve_multiplexed_model_id": str("large-v2")})
time.sleep(1)
answer = requests.post("http://localhost:8081/asr/2", json=json.dumps(file_name), headers={"serve_multiplexed_model_id": str("software-development")})
time.sleep(1)
answer = requests.post("http://localhost:8081/asr/1", json=json.dumps(file_name), headers={"serve_multiplexed_model_id": str("software-development")})
time.sleep(1)
answer = requests.post("http://localhost:8081/asr/2", json=json.dumps(file_name), headers={"serve_multiplexed_model_id": str("large-v2")})
print(json.loads(answer.text))


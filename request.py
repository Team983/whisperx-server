import requests
import json
import time

file_name = {"file_name":"2023-09-19T08-22-20.893072774_(1209).webm"}
# answer = requests.post("http://localhost:8081/asr/1", json=json.dumps(file_name), headers={"serve_multiplexed_model_id": "large-v2"})
answer = requests.post("http://localhost:8000/asr/1", json=json.dumps(file_name), headers={"serve_multiplexed_model_id": str("GENERAL")})
# time.sleep(1)
# answer = requests.post("http://localhost:8000/asr/2", json=json.dumps(file_name), headers={"serve_multiplexed_model_id": str("IT")})
# time.sleep(1)
# answer = requests.post("http://localhost:8000/asr/3", json=json.dumps(file_name), headers={"serve_multiplexed_model_id": str("IT")})
# time.sleep(1)
# answer = requests.post("http://localhost:8000/asr/4", json=json.dumps(file_name), headers={"serve_multiplexed_model_id": str("GENERAL")})
print(json.loads(answer.text))


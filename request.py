import requests
import json
import time
file_name = {"file_name":"c43f05f7-821c-4336-92b3-d98007e0f7f0"}
# answer = requests.post("http://localhost:8081/asr/1", json=json.dumps(file_name), headers={"serve_multiplexed_model_id": "large-v2"})
# answer = requests.post("https://team983.site/asr/1", json=json.dumps(file_name), headers={"serve_multiplexed_model_id": str("GENERAL")})
# time.sleep(1)
answer = requests.post("http://localhost:8000/asr/2", json=json.dumps(file_name), headers={"serve_multiplexed_model_id": str("IT")})
# time.sleep(1)
# answer = requests.post("http://localhost:8000/asr/3", json=json.dumps(file_name), headers={"serve_multiplexed_model_id": str("IT")})
# time.sleep(1)
# answer = requests.post("http://localhost:8000/asr/4", json=json.dumps(file_name), headers={"serve_multiplexed_model_id": str("GENERAL")})


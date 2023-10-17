import requests
import json
import time
file_name = {"file_name":"8765071f-090b-44d2-b561-ca5a7514a4aa", "model_type":"IT"}
# answer = requests.post("http://localhost:8081/asr/1", json=json.dumps(file_name), headers={"serve_multiplexed_model_id": "large-v2"})
# answer = requests.post("https://team983.site/asr/1", json=json.dumps(file_name), headers={"multiplexed_model_id": "GENERAL"})
# time.sleep(1)
answer = requests.post("http://localhost:8000/asr/2", json=json.dumps(file_name))
# time.sleep(1)
# answer = requests.post("http://localhost:8000/asr/3", json=json.dumps(file_name), headers={"serve_multiplexed_model_id": str("IT")})
# time.sleep(1)
# answer = requests.post("http://localhost:8000/asr/4", json=json.dumps(file_name), headers={"serve_multiplexed_model_id": str("GENERAL")})


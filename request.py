import requests
import json
import time
file_name = {"file_name":"f1a43991-e4fc-40cb-850a-f2041b9d594c.m4a"}
# answer = requests.post("http://localhost:8081/asr/1", json=json.dumps(file_name), headers={"serve_multiplexed_model_id": "large-v2"})
answer = requests.post("https://team983.site/asr/1", json=json.dumps(file_name), headers={"serve_multiplexed_model_id": "GENERAL"})
# time.sleep(1)
# answer = requests.post("http://localhost:8000/asr/2", json=json.dumps(file_name), headers={"serve_multiplexed_model_id": str("IT")})
# time.sleep(1)
# answer = requests.post("http://localhost:8000/asr/3", json=json.dumps(file_name), headers={"serve_multiplexed_model_id": str("IT")})
# time.sleep(1)
# answer = requests.post("http://localhost:8000/asr/4", json=json.dumps(file_name), headers={"serve_multiplexed_model_id": str("GENERAL")})


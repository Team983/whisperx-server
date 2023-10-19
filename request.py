import requests
import json

file_name = {"filename":"43abe690-97df-4a4d-aea0-abace6b71fc3", "category":"GENERAL"}
# answer = requests.post("http://localhost:8081/asr/1", json=json.dumps(file_name), headers={"serve_multiplexed_model_id": "large-v2"})
# answer = requests.post("https://team983.site/asr/1", json=json.dumps(file_name))
# time.sleep(1)
answer = requests.post("http://localhost:8000/asr/2", json=json.dumps(file_name))
# time.sleep(1)
# answer = requests.post("http://localhost:8000/asr/3", json=json.dumps(file_name), headers={"serve_multiplexed_model_id": str("IT")})
# time.sleep(1)
# answer = requests.post("http://localhost:8000/asr/4", json=json.dumps(file_name), headers={"serve_multiplexed_model_id": str("GENERAL")})
print(answer.text)

import requests
import json

file_name = {"filename":"6503c81a-6195-46d5-af21-af2fa79845ad", "category":"GENERAL"}
# answer = requests.post("http://localhost:8081/asr/1", json=json.dumps(file_name), headers={"serve_multiplexed_model_id": "large-v2"})
answer = requests.post("https://team983.site/asr/1", json=json.dumps(file_name))
# time.sleep(1)
# answer = requests.post("http://localhost:8000/asr/2", json=json.dumps(file_name))
# time.sleep(1)
# answer = requests.post("http://localhost:8000/asr/3", json=json.dumps(file_name), headers={"serve_multiplexed_model_id": str("IT")})
# time.sleep(1)
# answer = requests.post("http://localhost:8000/asr/4", json=json.dumps(file_name), headers={"serve_multiplexed_model_id": str("GENERAL")})
print(answer.text)

import requests
import json
import time
file_name = {"filename":"90d5da1a-54cf-4d83-9585-7f0ea2050104", "category":"IT"}
# answer = requests.post("http://localhost:8081/asr/1", json=json.dumps(file_name), headers={"serve_multiplexed_model_id": "large-v2"})
answer = requests.post("https://team983.site/asr/1", json=json.dumps(file_name))
# time.sleep(1)
# answer = requests.post("http://localhost:8000/asr/2", json=json.dumps(file_name))
# time.sleep(1)
# answer = requests.post("http://localhost:8000/asr/3", json=json.dumps(file_name), headers={"serve_multiplexed_model_id": str("IT")})
# time.sleep(1)
# answer = requests.post("http://localhost:8000/asr/4", json=json.dumps(file_name), headers={"serve_multiplexed_model_id": str("GENERAL")})
print(json.loads(answer))

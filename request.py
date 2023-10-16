import requests
import json
import time
# {“file_name”:“c19606c2-924c-43b7-8b64-093a7c60c374"}
{'file_name': 'd84942af-0d92-41f9-8515-8966e258972a'}
file_name = {"file_name":"d84942af-0d92-41f9-8515-8966e258972a'}
# answer = requests.post("http://localhost:8081/asr/1", json=json.dumps(file_name), headers={"serve_multiplexed_model_id": "large-v2"})
answer = requests.post("http://team983.site:8000/asr/1", json=json.dumps(file_name), headers={"serve_multiplexed_model_id": str("GENERAL")})
# time.sleep(1)
# answer = requests.post("http://localhost:8000/asr/2", json=json.dumps(file_name), headers={"serve_multiplexed_model_id": str("IT")})
# time.sleep(1)
# answer = requests.post("http://localhost:8000/asr/3", json=json.dumps(file_name), headers={"serve_multiplexed_model_id": str("IT")})
# time.sleep(1)
# answer = requests.post("http://localhost:8000/asr/4", json=json.dumps(file_name), headers={"serve_multiplexed_model_id": str("GENERAL")})
print(json.loads(answer.text))


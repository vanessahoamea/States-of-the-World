import requests
import json

response = requests.get(
    url="http://localhost:5000/top-10/area"
)
response_json = json.loads(response.text)
response_json = json.dumps(response_json, indent=2)
print(response_json)
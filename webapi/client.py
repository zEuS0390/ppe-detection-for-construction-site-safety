import requests

endpoint = "http://localhost:8000/api/listofviolators"

response = requests.get(endpoint)

print(response.json())
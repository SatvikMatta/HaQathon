#!/usr/bin/env python3

import requests

url = "http://localhost:3001/api/v1/auth"
headers = {
    "accept": "application/json",
    "Authorization": "Bearer N0J6HM4-6DB4CAP-K6WQ0HA-SP35QZ2"
}

response = requests.get(url, headers=headers)

print(f"Status Code: {response.status_code}")
print(f"Response: {response.json()}")
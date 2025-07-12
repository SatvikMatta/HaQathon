#!/usr/bin/env python3

import requests

url = "http://localhost:3001/api/v1/auth"
headers = {
    "accept": "application/json",
    "Authorization": "Bearer 156153F-4J1MSJ2-PZE4NHP-12R60AH"
}

response = requests.get(url, headers=headers)

print(f"Status Code: {response.status_code}")
print(f"Response: {response.json()}")
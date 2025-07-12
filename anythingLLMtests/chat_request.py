#!/usr/bin/env python3

import requests
import json

# Configuration
base_url = "http://localhost:3001"
workspace_slug = "haqathon"  # Replace with your workspace slug
api_token = "156153F-4J1MSJ2-PZE4NHP-12R60AH"

# Chat endpoint
chat_url = f"{base_url}/api/v1/workspace/{workspace_slug}/chat"

headers = {
    "accept": "application/json",
    "Content-Type": "application/json",
    "Authorization": f"Bearer {api_token}"
}

# System prompt for task monitoring
system_prompt = """Given the images provided and the task provided, provide a one word answer answering the question if the user is on task or is not on task.

DO NOT ASK QUESTIONS OR CLARIFICATIONS
DO NOT DO ANYTHING BUT ANSWER 'Yes' or 'No'"""

# Chat message payload - try without attachments first
payload = {
    "message": system_prompt,
    "mode": "chat"
}

try:
    response = requests.post(chat_url, headers=headers, json=payload)
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"Response: {json.dumps(result, indent=2)}")
    else:
        print(f"Error: {response.text}")
        
except requests.exceptions.RequestException as e:
    print(f"Request failed: {e}")
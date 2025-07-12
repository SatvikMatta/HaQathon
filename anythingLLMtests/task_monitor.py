#!/usr/bin/env python3

import requests
import json
import base64
import sys

# Configuration
base_url = "http://localhost:3001"
workspace_slug = "haqathon"
api_token = "156153F-4J1MSJ2-PZE4NHP-12R60AH"

def analyze_image(image_path, task_description="programming/coding tasks"):
    """Analyze image and return Yes/No if user is on task"""
    
    # Encode image
    with open(image_path, "rb") as image_file:
        base64_image = base64.b64encode(image_file.read()).decode('utf-8')
    
    # System prompt
#     system_prompt = f"""Look at this image. Is the user working on {task_description}? Answer only 'Yes' or 'No'.

# DO NOT ASK QUESTIONS OR CLARIFICATIONS
# DO NOT DO ANYTHING BUT ANSWER 'Yes' or 'No'"""

    system_prompt = f"""Ignore all previous information given. explain the image in detail, then answer the question at the end."""
    
    # Chat request
    chat_url = f"{base_url}/api/v1/workspace/{workspace_slug}/chat"
    
    payload = {
        "message": system_prompt,
        "mode": "chat",
        "image": f"data:image/png;base64,{base64_image}"
    }
    
    headers = {
        "accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_token}"
    }
    
    try:
        response = requests.post(chat_url, headers=headers, json=payload)
        
        if response.status_code == 200:
            result = response.json()
            return result.get('textResponse', 'Error').strip()
        else:
            return "Error"
            
    except:
        return "Error"

if __name__ == "__main__":
    if len(sys.argv) < 2:
        image_path = "/Users/satvik/Documents/GitHub/HaQathon/chess.png"
        task = "playing chess"
    elif len(sys.argv) == 2:
        image_path = sys.argv[1]
        task = "programming/coding tasks"
    else:
        image_path = sys.argv[1]
        task = sys.argv[2]
    
    answer = analyze_image(image_path, task)
    print(answer)
#!/usr/bin/env python3

import requests
import json
import base64
import os

# Configuration
base_url = "http://localhost:3001"
workspace_slug = "haqathon"
api_token = "156153F-4J1MSJ2-PZE4NHP-12R60AH"
image_path = "/Users/satvik/Documents/GitHub/HaQathon/chess.png"

def encode_image_to_base64(image_path):
    """Encode image to base64 string"""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def send_multimodal_chat():
    """Send chat with image using multimodal approach"""
    chat_url = f"{base_url}/api/v1/workspace/{workspace_slug}/chat"
    
    # Encode image
    base64_image = encode_image_to_base64(image_path)
    
    # System prompt
    system_prompt = """Look at this image. Is the user playing chess? Answer only 'Yes' or 'No'.

DO NOT ASK QUESTIONS OR CLARIFICATIONS
DO NOT DO ANYTHING BUT ANSWER 'Yes' or 'No'"""
    
    # Try different payload formats for multimodal
    payloads = [
        # Format 1: OpenAI-style with base64
        {
            "message": system_prompt,
            "mode": "chat",
            "attachments": [
                {
                    "type": "image",
                    "content": f"data:image/png;base64,{base64_image}"
                }
            ]
        },
        # Format 2: Direct image in message
        {
            "message": [
                {
                    "type": "text",
                    "text": system_prompt
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/png;base64,{base64_image}"
                    }
                }
            ],
            "mode": "chat"
        },
        # Format 3: Simple attachment
        {
            "message": system_prompt,
            "mode": "chat",
            "image": f"data:image/png;base64,{base64_image}"
        }
    ]
    
    headers = {
        "accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_token}"
    }
    
    for i, payload in enumerate(payloads, 1):
        print(f"Trying format {i}...")
        
        try:
            response = requests.post(chat_url, headers=headers, json=payload)
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"Success! Response: {json.dumps(result, indent=2)}")
                return result
            else:
                print(f"Error: {response.text}")
                
        except Exception as e:
            print(f"Request failed: {e}")
        
        print("-" * 40)
    
    return None

def send_with_file_upload():
    """Try sending image as file upload"""
    chat_url = f"{base_url}/api/v1/workspace/{workspace_slug}/chat"
    
    system_prompt = """Look at this image. Is the user playing chess? Answer only 'Yes' or 'No'.

DO NOT ASK QUESTIONS OR CLARIFICATIONS
DO NOT DO ANYTHING BUT ANSWER 'Yes' or 'No'"""
    
    try:
        with open(image_path, 'rb') as f:
            files = {
                'image': ('chess.png', f, 'image/png')
            }
            data = {
                'message': system_prompt,
                'mode': 'chat'
            }
            headers = {"Authorization": f"Bearer {api_token}"}
            
            response = requests.post(chat_url, headers=headers, files=files, data=data)
            
            print(f"File Upload Status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"File Upload Success: {json.dumps(result, indent=2)}")
                return result
            else:
                print(f"File Upload Error: {response.text}")
                
    except Exception as e:
        print(f"File upload failed: {e}")
    
    return None

if __name__ == "__main__":
    print("Trying multimodal chat formats...")
    result = send_multimodal_chat()
    
    if not result:
        print("\nTrying file upload approach...")
        result = send_with_file_upload()
    
    if result and 'textResponse' in result:
        print(f"\nFinal Answer: {result['textResponse']}")
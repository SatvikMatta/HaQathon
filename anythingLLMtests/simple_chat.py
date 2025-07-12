#!/usr/bin/env python3

import requests
import json
import pytesseract as tesseract

# Configuration
base_url = "http://localhost:3001"
workspace_slug = "haqathon"
api_token = "156153F-4J1MSJ2-PZE4NHP-12R60AH"

# Use the OCR text directly from the screenshot
screenshot_content = ''

# Use Tesseract to extract text from the screenshot
image_path = '/Users/satvik/Documents/GitHub/HaQathon/chess.png'
try:
    screenshot_content = tesseract.image_to_string(image_path)
    # print(f"Extracted text from screenshot: {screenshot_content}")
except Exception as e:
    print(f"Error extracting text from screenshot: {e}") 



# System prompt with the screenshot content
system_prompt = f"""Based on this screenshot content from VS Code:

{screenshot_content}

Is the user working on Playing Chess? Answer only 'Yes' or 'No'.

DO NOT ASK QUESTIONS OR CLARIFICATIONS
DO NOT DO ANYTHING BUT ANSWER 'Yes' or 'No'"""

# Chat endpoint
chat_url = f"{base_url}/api/v1/workspace/{workspace_slug}/chat"

headers = {
    "accept": "application/json",
    "Content-Type": "application/json",
    "Authorization": f"Bearer {api_token}"
}

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
        
        # Extract just the answer
        if 'textResponse' in result:
            print(f"\nAnswer: {result['textResponse']}")
    else:
        print(f"Error: {response.text}")
        
except requests.exceptions.RequestException as e:
    print(f"Request failed: {e}")
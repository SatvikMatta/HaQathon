#!/usr/bin/env python3

import requests
import json
import base64

# Configuration
base_url = "http://localhost:3001"
workspace_slug = "haqathon"
api_token = "N0J6HM4-6DB4CAP-K6WQ0HA-SP35QZ2"
image_path = "anythingLLMtests/chess.png"

headers = {
    "accept": "application/json",
    "Authorization": f"Bearer {api_token}"
}

# System prompt for task monitoring
system_prompt = """Analyze this screenshot image carefully.

Based on what you see in this screenshot, is the user working on programming/coding tasks? Answer only 'Yes' or 'No'.

DO NOT ASK QUESTIONS OR CLARIFICATIONS
DO NOT DO ANYTHING BUT ANSWER 'Yes' or 'No'"""

def upload_file_to_workspace():
    """Upload image file to workspace"""
    upload_url = f"{base_url}/api/v1/document/upload"
    
    try:
        with open(image_path, 'rb') as f:
            files = {'file': f}
            upload_headers = {"Authorization": f"Bearer {api_token}"}
            
            response = requests.post(upload_url, headers=upload_headers, files=files)
            print(f"Upload Status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"Upload Response: {json.dumps(result, indent=2)}")
                return result
            else:
                print(f"Upload Error: {response.text}")
                return None
                
    except Exception as e:
        print(f"Upload failed: {e}")
        return None

def send_chat_with_image():
    """Send chat message with image as multipart"""
    chat_url = f"{base_url}/api/v1/workspace/{workspace_slug}/chat"
    
    try:
        with open(image_path, 'rb') as f:
            files = {
                'file': ('screenshot.png', f, 'image/png')
            }
            data = {
                'message': system_prompt,
                'mode': 'chat'
            }
            chat_headers = {"Authorization": f"Bearer {api_token}"}
            
            response = requests.post(chat_url, headers=chat_headers, files=files, data=data)
            
            print(f"Chat Status Code: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"Chat Response: {json.dumps(result, indent=2)}")
            else:
                print(f"Chat Error: {response.text}")
                
    except Exception as e:
        print(f"Chat request failed: {e}")

def send_chat_with_base64():
    """Alternative: Send chat with base64 encoded image"""
    chat_url = f"{base_url}/api/v1/workspace/{workspace_slug}/chat"
    
    try:
        with open(image_path, 'rb') as f:
            image_data = base64.b64encode(f.read()).decode('utf-8')
        
        payload = {
            "message": system_prompt,
            "mode": "chat",
            "attachments": [{
                "type": "image",
                "data": f"data:image/png;base64,{image_data}"
            }]
        }
        
        chat_headers = {
            "accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_token}"
        }
        
        response = requests.post(chat_url, headers=chat_headers, json=payload)
        
        print(f"Base64 Chat Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Base64 Response: {json.dumps(result, indent=2)}")
        else:
            print(f"Base64 Error: {response.text}")
            
    except Exception as e:
        print(f"Base64 chat failed: {e}")

if __name__ == "__main__":
    print("Trying multipart upload with message...")
    send_chat_with_image()
    
    print("\n" + "="*50 + "\n")
    
    print("Trying base64 encoded image...")
    send_chat_with_base64()
    
    print("\n" + "="*50 + "\n")
    
    print("Trying separate upload then chat...")
    upload_result = upload_file_to_workspace()
    
    if upload_result and upload_result.get('success'):
        doc_id = upload_result['documents'][0]['id']
        print(f"Document uploaded with ID: {doc_id}")
        
        # Embed document into workspace
        embed_url = f"{base_url}/api/v1/workspace/{workspace_slug}/update-embeddings"
        embed_payload = {
            "adds": [doc_id],
            "deletes": []
        }
        embed_headers = {
            "accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_token}"
        }
        
        embed_response = requests.post(embed_url, headers=embed_headers, json=embed_payload)
        print(f"Embed Status: {embed_response.status_code}")
        
        if embed_response.status_code == 200:
            print("Document embedded successfully")
            
            # Now chat with the embedded document
            chat_url = f"{base_url}/api/v1/workspace/{workspace_slug}/chat"
            chat_payload = {
                "message": system_prompt,
                "mode": "query"  # Use query mode to reference documents
            }
            
            chat_response = requests.post(chat_url, headers=embed_headers, json=chat_payload)
            print(f"Final Chat Status: {chat_response.status_code}")
            
            if chat_response.status_code == 200:
                result = chat_response.json()
                print(f"Final Chat Response: {json.dumps(result, indent=2)}")
            else:
                print(f"Final Chat Error: {chat_response.text}")
        else:
            print(f"Embed Error: {embed_response.text}")
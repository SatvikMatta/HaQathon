import pytesseract
from PIL import Image
# Make sure to install Pytesseract and Verify This Path
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'


import requests
import json
import time
import sys
import os
from datetime import datetime
from typing import Dict, Any, Optional, Callable
from PIL import ImageGrab
from PIL.Image import Image
            
def get_text_from_screenshot(image: Image) -> str:
    if image is None:
        return "No Image Provided"
    extracted_text = pytesseract.image_to_string(image)
    return extracted_text

# Configuration
BASE_URL = "http://localhost:3001"
WORKSPACE_SLUG = "haqathon"
# API_TOKEN = "N0J6HM4-6DB4CAP-K6WQ0HA-SP35QZ2"
API_TOKEN = "EG6KWET-JB7MRZT-PEVAWQ1-PWVJ88Q"


def classify_task(task) -> Dict[str, Any]:
    system_prompt = f"""
    Here is the Task: {task}
    Classify the task as one of the following:
- PROGRAMMING: Code, programming languages, IDEs, GitHub, Stack Overflow, coding tutorials, development tools
- WEB_BROWSING: General web browsing, news sites
- GAMING: Video games, gaming websites, game launchers, gaming content
- PRODUCTIVITY: Documents, spreadsheets, presentations, email, calendar, office work, business apps
- MEDIA: Video streaming, music, entertainment content, YouTube, Netflix
- COMMUNICATION: Chat apps, messaging, video calls, meetings, social platforms for communication
- LEARNING: Educational content, tutorials, courses, documentation, research, learning platforms

Look for specific keywords, application names, programming languages, code snippets, website names, etc.
YouTube, Netfilx, Hulu, etc. is ALWAYS MEDIA

Respond in this exact JSON format:
{{
"category": "CATEGORY_NAME",
"confidence": 0.95,
"key_indicators": ["list", "of", "key", "words", "or", "phrases", "that", "led", "to", "this", "classification"],
}}

                        DO NOT include any text outside the JSON response.
"""
    try:
        # Prepare the request
        chat_url = f"{BASE_URL}/api/v1/workspace/{WORKSPACE_SLUG}/chat"
        payload = {
            "message": system_prompt,
            "mode": "chat"
        }
        headers = {
            "accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {API_TOKEN}"
        }
        
        # Send the request
        response = requests.post(chat_url, headers=headers, json=payload)
        
        if response.status_code == 200:
            result = response.json()
            return {
                "success": True,
                "classification": result.get("textResponse", ""),
                "metrics": result.get("metrics", {}),
                "timestamp": datetime.now().isoformat(),
            }
        else:
            return {
                "success": False,
                "error": f"API Error: {response.status_code} - {response.text}",
                "timestamp": datetime.now().isoformat()
            }
    except Exception as e:
        return {
            "success": False,
            "error": f"Classification failed: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }

def classify_activity_from_text(extracted_text: str, clip) -> Dict[str, Any]:
    """Classify the activity based on extracted text content"""
    
    # Create a comprehensive classification prompt for text analysis
    system_prompt = f"""
    IGNORE ALL PREVIOUS KNOWLEGE.
    Analyze this text content extracted from a user's screen via OCR and classify their current activity.
TEXT CONTENT FROM SCREEN:
{extracted_text}

HERE IS EXTRA INFO THAT MAY NOT BE RIGHT:
Estimated Screen Category: {clip}

Based on the text content above, classify the user's activity into ONE of these categories:
- PROGRAMMING: Code, programming languages, IDEs, GitHub, Stack Overflow, coding tutorials, development tools
- WEB_BROWSING: General web browsing, news sites
- GAMING: Video games, gaming websites, game launchers, gaming content
- PRODUCTIVITY: Documents, spreadsheets, presentations, email, calendar, office work, business apps
- MEDIA: Video streaming, music, entertainment content, YouTube, Netflix
- COMMUNICATION: Chat apps, messaging, video calls, meetings, social platforms for communication
- LEARNING: Educational content, tutorials, courses, documentation, research, learning platforms
- IDLE: Desktop, minimal content, screensaver, system interfaces
- OTHER: Unclear, mixed activities, or doesn't fit other categories

Look for specific keywords, application names, programming languages, code snippets, website names, etc.
YouTube, Netfilx, Hulu, etc. is ALWAYS MEDIA

IF is Productive -> Focus Level high or medium
IF NOT Productive -> Focus Level medium or low


Respond in this exact JSON format:
{{
"category": "CATEGORY_NAME",
"confidence": 0.95,
"description": "Brief description of what the user is doing based on the text",
"key_indicators": ["list", "of", "key", "words", "or", "phrases", "that", "led", "to", "this", "classification"],
"is_productive": true/false,
"focus_level": "high/medium/low"
}}

                        DO NOT include any text outside the JSON response."""
    try:
        # Prepare the request
        chat_url = f"{BASE_URL}/api/v1/workspace/{WORKSPACE_SLUG}/chat"
        payload = {
            "message": system_prompt,
            "mode": "chat"
        }
        headers = {
            "accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {API_TOKEN}"
        }
        
        # Send the request
        response = requests.post(chat_url, headers=headers, json=payload)
        
        if response.status_code == 200:
            result = response.json()
            return {
                "success": True,
                "classification": result.get("textResponse", ""),
                "metrics": result.get("metrics", {}),
                "timestamp": datetime.now().isoformat(),
                "extracted_text_length": len(extracted_text)
            }
        else:
            return {
                "success": False,
                "error": f"API Error: {response.status_code} - {response.text}",
                "timestamp": datetime.now().isoformat()
            }
            
    except Exception as e:
        return {
            "success": False,
            "error": f"Classification failed: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }

# List of focus
def screenshot():
    return ImageGrab.grab()

def get_json_screenshot(screenshot: Image, clip_input: str):
    screenshot_text = get_text_from_screenshot(screenshot)
    return classify_activity_from_text(extracted_text=screenshot_text, clip=clip_input)

def get_json_task(given_task: str):
    if given_task is None:
        return None
    task_class = classify_task(task=given_task)
    return task_class



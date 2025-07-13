#!/usr/bin/env python3

import requests
import json
import base64
import time
import sys
import os
from datetime import datetime
from typing import Dict, Any, Optional

# Configuration
BASE_URL = "http://localhost:3001"
WORKSPACE_SLUG = "haqathon"
API_TOKEN = "N0J6HM4-6DB4CAP-K6WQ0HA-SP35QZ2"

# Activity categories for classification
ACTIVITY_CATEGORIES = {
    "programming": ["coding", "development", "programming", "IDE", "text editor", "terminal", "command line"],
    "web_browsing": ["web browser", "browsing", "internet", "website", "social media", "news"],
    "gaming": ["game", "gaming", "video game", "entertainment", "play"],
    "productivity": ["document", "spreadsheet", "presentation", "email", "calendar", "office"],
    "media": ["video", "music", "streaming", "media player", "youtube", "netflix"],
    "communication": ["chat", "messaging", "video call", "meeting", "zoom", "teams"],
    "learning": ["tutorial", "course", "education", "reading", "documentation", "learning"],
    "idle": ["desktop", "screensaver", "idle", "nothing", "blank"],
    "other": ["unknown", "unclear", "mixed", "various"]
}

class ScreenActivityClassifier:
    def __init__(self):
        self.headers = {
            "accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {API_TOKEN}"
        }
        
        # Try to import screenshot libraries
        self.screenshot_method = self._detect_screenshot_method()
        
    def _detect_screenshot_method(self) -> str:
        """Detect which screenshot method is available"""
        try:
            import pyautogui
            return "pyautogui"
        except ImportError:
            try:
                from PIL import ImageGrab
                return "pillow"
            except ImportError:
                return "none"
    
    def take_screenshot(self, save_path: str = "temp_screenshot.png", full_screen: bool = True) -> bool:
        """Take a screenshot and save it"""
        try:
            if self.screenshot_method == "pyautogui":
                import pyautogui
                screenshot = pyautogui.screenshot()
                screenshot.save(save_path)
                return True
            elif self.screenshot_method == "pillow":
                from PIL import ImageGrab
                
                # Always take full screen for better accuracy
                # The partial window capture was causing issues
                screenshot = ImageGrab.grab()
                screenshot.save(save_path)
                return True
            else:
                print("Error: No screenshot library available. Install pyautogui or PIL.")
                return False
        except Exception as e:
            print(f"Screenshot failed: {e}")
            return False
    
    def classify_activity(self, image_path: str) -> Dict[str, Any]:
        """Classify the activity shown in the screenshot"""
        
        # Create a comprehensive classification prompt
        system_prompt = """Analyze this screenshot image carefully and classify the user's current activity.

Look at the applications, windows, content, and context visible in the screenshot.

Classify the activity into ONE of these categories:
- PROGRAMMING: Coding, development, IDEs, text editors, terminals, GitHub, code repositories
- WEB_BROWSING: Web browsers, social media, news sites, general internet browsing
- GAMING: Video games, game launchers, gaming websites, entertainment
- PRODUCTIVITY: Documents, spreadsheets, presentations, email, calendar, office work
- MEDIA: Video streaming, music, media players, YouTube, Netflix, entertainment content
- COMMUNICATION: Chat apps, messaging, video calls, meetings, Zoom, Teams, Discord
- LEARNING: Educational content, tutorials, courses, documentation, research
- IDLE: Desktop, screensaver, minimal activity, blank screens
- OTHER: Unclear, mixed activities, or doesn't fit other categories

Respond in this exact JSON format:
{
  "category": "CATEGORY_NAME",
  "confidence": 0.95,
  "description": "Brief description of what the user is doing",
  "details": "More specific details about the applications and content visible",
  "is_productive": true/false,
  "focus_level": "high/medium/low"
}

DO NOT include any text outside the JSON response."""

        try:
            # Read and encode the image
            with open(image_path, 'rb') as f:
                image_data = base64.b64encode(f.read()).decode('utf-8')
            
            # Prepare the request
            chat_url = f"{BASE_URL}/api/v1/workspace/{WORKSPACE_SLUG}/chat"
            payload = {
                "message": system_prompt,
                "mode": "chat",
                "attachments": [{
                    "type": "image",
                    "data": f"data:image/png;base64,{image_data}"
                }]
            }
            
            # Send the request
            response = requests.post(chat_url, headers=self.headers, json=payload)
            
            if response.status_code == 200:
                result = response.json()
                return {
                    "success": True,
                    "classification": result.get("textResponse", ""),
                    "metrics": result.get("metrics", {}),
                    "timestamp": datetime.now().isoformat()
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
    
    def parse_classification_result(self, classification_text: str) -> Dict[str, Any]:
        """Parse the JSON classification result"""
        try:
            # Try to extract JSON from the response
            import re
            json_match = re.search(r'\{.*\}', classification_text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            else:
                return {"error": "No valid JSON found in response"}
        except json.JSONDecodeError:
            return {"error": "Invalid JSON in response", "raw_response": classification_text}
    
    def monitor_activity(self, duration_seconds: int = 60, interval_seconds: int = 10):
        """Monitor user activity for a specified duration"""
        print(f"🔍 Starting activity monitoring for {duration_seconds} seconds...")
        print(f"📸 Taking screenshots every {interval_seconds} seconds")
        print(f"📊 Screenshot method: {self.screenshot_method}")
        print("-" * 60)
        
        if self.screenshot_method == "none":
            print("❌ Cannot monitor - no screenshot library available")
            return
        
        start_time = time.time()
        results = []
        
        while time.time() - start_time < duration_seconds:
            try:
                timestamp = datetime.now().strftime("%H:%M:%S")
                print(f"[{timestamp}] Taking screenshot...")
                
                # Take screenshot
                screenshot_path = f"temp_screenshot_{int(time.time())}.png"
                if self.take_screenshot(screenshot_path):
                    
                    # Classify activity
                    print(f"[{timestamp}] Analyzing activity...")
                    result = self.classify_activity(screenshot_path)
                    
                    if result["success"]:
                        # Parse the classification
                        classification = self.parse_classification_result(result["classification"])
                        
                        if "error" not in classification:
                            print(f"[{timestamp}] 🎯 Activity: {classification.get('category', 'Unknown')}")
                            print(f"[{timestamp}] 📝 Description: {classification.get('description', 'No description')}")
                            print(f"[{timestamp}] 🎚️ Confidence: {classification.get('confidence', 0):.2f}")
                            print(f"[{timestamp}] 🏆 Productive: {classification.get('is_productive', 'Unknown')}")
                            print(f"[{timestamp}] 🎯 Focus: {classification.get('focus_level', 'Unknown')}")
                            
                            # Add to results
                            results.append({
                                "timestamp": timestamp,
                                "classification": classification,
                                "metrics": result.get("metrics", {})
                            })
                        else:
                            print(f"[{timestamp}] ❌ Classification parsing failed: {classification.get('error', 'Unknown error')}")
                            if "raw_response" in classification:
                                print(f"[{timestamp}] 📄 Raw response: {classification['raw_response'][:200]}...")
                    else:
                        print(f"[{timestamp}] ❌ Classification failed: {result.get('error', 'Unknown error')}")
                    
                    # Clean up screenshot
                    try:
                        os.remove(screenshot_path)
                    except:
                        pass
                else:
                    print(f"[{timestamp}] ❌ Screenshot failed")
                
                print("-" * 60)
                
                # Wait for next interval
                time.sleep(interval_seconds)
                
            except KeyboardInterrupt:
                print("\n⏹️ Monitoring stopped by user")
                break
            except Exception as e:
                print(f"[{timestamp}] ❌ Error: {str(e)}")
                time.sleep(interval_seconds)
        
        # Summary
        print(f"\n📊 MONITORING SUMMARY ({len(results)} samples)")
        print("=" * 60)
        
        if results:
            categories = {}
            total_confidence = 0
            productive_count = 0
            
            for result in results:
                classification = result["classification"]
                category = classification.get("category", "Unknown")
                confidence = classification.get("confidence", 0)
                is_productive = classification.get("is_productive", False)
                
                categories[category] = categories.get(category, 0) + 1
                total_confidence += confidence
                if is_productive:
                    productive_count += 1
            
            print("📈 Activity Distribution:")
            for category, count in sorted(categories.items()):
                percentage = (count / len(results)) * 100
                print(f"  {category}: {count} samples ({percentage:.1f}%)")
            
            print(f"\n🎯 Average Confidence: {total_confidence/len(results):.2f}")
            print(f"🏆 Productive Time: {productive_count}/{len(results)} samples ({(productive_count/len(results))*100:.1f}%)")
        else:
            print("❌ No successful classifications recorded")


def main():
    """Main function to run the screen activity classifier"""
    classifier = ScreenActivityClassifier()
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "monitor":
            # Monitor mode
            duration = int(sys.argv[2]) if len(sys.argv) > 2 else 60
            interval = int(sys.argv[3]) if len(sys.argv) > 3 else 10
            classifier.monitor_activity(duration, interval)
        elif sys.argv[1] == "single":
            # Single screenshot mode
            image_path = sys.argv[2] if len(sys.argv) > 2 else "temp_screenshot.png"
            
            if len(sys.argv) <= 2:
                print("📸 Taking screenshot...")
                if not classifier.take_screenshot(image_path):
                    print("❌ Failed to take screenshot")
                    return
            
            print("🔍 Classifying activity...")
            result = classifier.classify_activity(image_path)
            
            if result["success"]:
                classification = classifier.parse_classification_result(result["classification"])
                print(f"\n📊 CLASSIFICATION RESULT:")
                print("=" * 40)
                print(json.dumps(classification, indent=2))
                print(f"\n⚡ Processing time: {result['metrics'].get('duration', 'Unknown')} seconds")
            else:
                print(f"❌ Classification failed: {result['error']}")
        else:
            print("❌ Unknown command. Use 'monitor' or 'single'")
    else:
        # Default: single screenshot
        print("📸 Taking screenshot and classifying...")
        if classifier.take_screenshot("temp_screenshot.png"):
            result = classifier.classify_activity("temp_screenshot.png")
            
            if result["success"]:
                classification = classifier.parse_classification_result(result["classification"])
                print(f"\n📊 CURRENT ACTIVITY:")
                print("=" * 40)
                print(json.dumps(classification, indent=2))
            else:
                print(f"❌ Classification failed: {result['error']}")
        else:
            print("❌ Failed to take screenshot")


if __name__ == "__main__":
    main() 
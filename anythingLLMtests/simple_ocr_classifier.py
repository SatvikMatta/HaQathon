#!/usr/bin/env python3

import requests
import json
import base64
import time
import sys
import os
from datetime import datetime
from typing import Dict, Any

# Configuration
BASE_URL = "http://localhost:3001"
WORKSPACE_SLUG = "haqathon"
API_TOKEN = "N0J6HM4-6DB4CAP-K6WQ0HA-SP35QZ2"

class SimpleOCRClassifier:
    def __init__(self):
        self.headers = {
            "accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {API_TOKEN}"
        }
        
        # Check screenshot capability
        self.screenshot_method = self._detect_screenshot_method()
        
    def _detect_screenshot_method(self) -> str:
        """Detect which screenshot method is available"""
        try:
            from PIL import ImageGrab
            return "pillow"
        except ImportError:
            try:
                import pyautogui
                return "pyautogui"
            except ImportError:
                return "none"
    
    def take_screenshot(self, save_path: str = "temp_screenshot.png") -> bool:
        """Take a screenshot and save it"""
        try:
            if self.screenshot_method == "pillow":
                from PIL import ImageGrab
                screenshot = ImageGrab.grab()
                screenshot.save(save_path)
                return True
            elif self.screenshot_method == "pyautogui":
                import pyautogui
                screenshot = pyautogui.screenshot()
                screenshot.save(save_path)
                return True
            else:
                print("Error: No screenshot library available.")
                return False
        except Exception as e:
            print(f"Screenshot failed: {e}")
            return False
    
    def analyze_activity_with_image_and_text_extraction(self, image_path: str) -> Dict[str, Any]:
        """Analyze activity using both image analysis and text extraction request"""
        
        # Create a comprehensive prompt that asks the LLM to extract text AND classify
        system_prompt = """Ignore all previous chat history. Only look at the current screenshot.
        
        Analyze this screenshot and do TWO things:

1. EXTRACT TEXT: Read and extract all visible text content from the image (like OCR)
2. CLASSIFY ACTIVITY: Based on both the visual elements and extracted text, classify the user's activity

Look for:
- Application names, window titles, UI elements
- Text content, code, website content, document text
- Programming languages, code snippets, terminal commands
- Website names, social media, browser content
- Any visible text that indicates what the user is doing

Classify the activity into ONE category:
- PROGRAMMING: Coding, IDEs, code editors, GitHub, Stack Overflow, development tools
- WEB_BROWSING: Web browsers, social media, news, entertainment websites
- GAMING: Video games, game launchers, gaming websites
- PRODUCTIVITY: Documents, spreadsheets, email, office work, business applications
- MEDIA: Video streaming, music players, entertainment content
- COMMUNICATION: Chat apps, messaging, video calls, social platforms
- LEARNING: Educational content, tutorials, documentation, courses
- IDLE: Desktop, minimal activity, system interfaces
- OTHER: Mixed or unclear activities

Respond in this exact JSON format:
{
  "extracted_text": "All the text content you can read from the image",
  "category": "CATEGORY_NAME",
  "confidence": 0.95,
  "description": "What the user is doing based on visual and text analysis",
  "key_indicators": ["specific", "text", "or", "visual", "elements", "that", "led", "to", "classification"],
  "applications_detected": ["list", "of", "applications", "or", "websites", "visible"],
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
                "error": f"Analysis failed: {str(e)}",
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
                return {"error": "No valid JSON found in response", "raw_response": classification_text}
        except json.JSONDecodeError:
            return {"error": "Invalid JSON in response", "raw_response": classification_text}
    
    def analyze_current_activity(self) -> Dict[str, Any]:
        """Take screenshot and analyze activity with text extraction"""
        print("📸 Taking screenshot...")
        
        screenshot_path = f"simple_ocr_screenshot_{int(time.time())}.png"
        
        if not self.take_screenshot(screenshot_path):
            return {"success": False, "error": "Failed to take screenshot"}
        
        print("🔍 Analyzing screenshot with integrated text extraction...")
        result = self.analyze_activity_with_image_and_text_extraction(screenshot_path)
        
        # Clean up screenshot
        try:
            os.remove(screenshot_path)
        except:
            pass
        
        return result
    
    def monitor_activity(self, duration_seconds: int = 60, interval_seconds: int = 20):
        """Monitor user activity using screenshot + text analysis"""
        print(f"🔍 Starting integrated OCR activity monitoring for {duration_seconds} seconds...")
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
                print(f"[{timestamp}] Analyzing activity...")
                
                result = self.analyze_current_activity()
                
                if result["success"]:
                    # Parse the classification
                    classification = self.parse_classification_result(result["classification"])
                    
                    if "error" not in classification:
                        print(f"[{timestamp}] 🎯 Activity: {classification.get('category', 'Unknown')}")
                        print(f"[{timestamp}] 📝 Description: {classification.get('description', 'No description')}")
                        print(f"[{timestamp}] 🎚️ Confidence: {classification.get('confidence', 0):.2f}")
                        print(f"[{timestamp}] 🔑 Key indicators: {', '.join(classification.get('key_indicators', [])[:3])}")
                        print(f"[{timestamp}] 💻 Apps detected: {', '.join(classification.get('applications_detected', [])[:2])}")
                        print(f"[{timestamp}] 🏆 Productive: {classification.get('is_productive', 'Unknown')}")
                        print(f"[{timestamp}] 🎯 Focus: {classification.get('focus_level', 'Unknown')}")
                        
                        # Show extracted text preview
                        extracted_text = classification.get('extracted_text', '')
                        if extracted_text and len(extracted_text) > 10:
                            preview = extracted_text[:100].replace('\n', ' ')
                            print(f"[{timestamp}] 📄 Text preview: {preview}...")
                        
                        # Add to results
                        results.append({
                            "timestamp": timestamp,
                            "classification": classification,
                            "metrics": result.get("metrics", {})
                        })
                    else:
                        print(f"[{timestamp}] ❌ Classification parsing failed: {classification.get('error', 'Unknown error')}")
                        if "raw_response" in classification:
                            print(f"[{timestamp}] 📄 Raw response preview: {classification['raw_response'][:200]}...")
                else:
                    print(f"[{timestamp}] ❌ Analysis failed: {result.get('error', 'Unknown error')}")
                
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
        print(f"\n📊 INTEGRATED OCR MONITORING SUMMARY ({len(results)} samples)")
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
    """Main function"""
    classifier = SimpleOCRClassifier()
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "monitor":
            # Monitor mode
            duration = int(sys.argv[2]) if len(sys.argv) > 2 else 60
            interval = int(sys.argv[3]) if len(sys.argv) > 3 else 20
            classifier.monitor_activity(duration, interval)
        elif sys.argv[1] == "single":
            # Single screenshot analysis
            image_path = sys.argv[2] if len(sys.argv) > 2 else None
            
            if image_path and os.path.exists(image_path):
                print(f"🔍 Analyzing provided image: {image_path}")
                result = classifier.analyze_activity_with_image_and_text_extraction(image_path)
            else:
                print("📸 Taking new screenshot for analysis...")
                result = classifier.analyze_current_activity()
            
            if result["success"]:
                classification = classifier.parse_classification_result(result["classification"])
                print(f"\n📊 ACTIVITY ANALYSIS RESULT:")
                print("=" * 40)
                if "error" not in classification:
                    print(json.dumps(classification, indent=2))
                    print(f"\n⚡ Processing time: {result['metrics'].get('duration', 'Unknown')} seconds")
                else:
                    print(f"❌ Classification parsing failed: {classification.get('error', 'Unknown error')}")
                    if "raw_response" in classification:
                        print(f"📄 Raw response: {classification['raw_response'][:500]}...")
            else:
                print(f"❌ Analysis failed: {result['error']}")
        else:
            print("❌ Unknown command. Use 'monitor' or 'single [image_path]'")
    else:
        # Default: single analysis
        print("🔤 Analyzing current screen with integrated text extraction...")
        result = classifier.analyze_current_activity()
        
        if result["success"]:
            classification = classifier.parse_classification_result(result["classification"])
            print(f"\n📊 CURRENT ACTIVITY (with text extraction):")
            print("=" * 50)
            if "error" not in classification:
                print(json.dumps(classification, indent=2))
                print(f"\n⚡ Processing time: {result['metrics'].get('duration', 'Unknown')} seconds")
            else:
                print(f"❌ Classification parsing failed: {classification.get('error', 'Unknown error')}")
                if "raw_response" in classification:
                    print(f"📄 Raw response: {classification['raw_response'][:500]}...")
        else:
            print(f"❌ Analysis failed: {result['error']}")


if __name__ == "__main__":
    main() 
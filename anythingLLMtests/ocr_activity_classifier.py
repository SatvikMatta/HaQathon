#!/usr/bin/env python3

import requests
import json
import time
import sys
import os
from datetime import datetime
from typing import Dict, Any, Optional

# Configuration
BASE_URL = "http://localhost:3001"
WORKSPACE_SLUG = "haqathon"
API_TOKEN = "N0J6HM4-6DB4CAP-K6WQ0HA-SP35QZ2"

class OCRActivityClassifier:
    def __init__(self):
        self.headers = {
            "accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {API_TOKEN}"
        }
        
        # Try to import required libraries
        self.screenshot_method = self._detect_screenshot_method()
        self.ocr_available = self._check_ocr_availability()
        
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
    
    def _check_ocr_availability(self) -> bool:
        """Check if OCR libraries are available"""
        try:
            import pytesseract
            return True
        except ImportError:
            return False
    
    def take_screenshot(self, save_path: str = "temp_screenshot.png") -> bool:
        """Take a screenshot and save it"""
        try:
            if self.screenshot_method == "pyautogui":
                import pyautogui
                screenshot = pyautogui.screenshot()
                screenshot.save(save_path)
                return True
            elif self.screenshot_method == "pillow":
                from PIL import ImageGrab
                screenshot = ImageGrab.grab()
                screenshot.save(save_path)
                return True
            else:
                print("Error: No screenshot library available. Install pyautogui or PIL.")
                return False
        except Exception as e:
            print(f"Screenshot failed: {e}")
            return False
    
    def extract_text_from_screenshot(self, image_path: str) -> str:
        """Extract text from screenshot using OCR"""
        if not self.ocr_available:
            return "OCR not available"
        
        try:
            import pytesseract
            from PIL import Image
            
            # Open the image
            image = Image.open(image_path)
            
            # Extract text using OCR
            extracted_text = pytesseract.image_to_string(image)
            
            # Clean up the text
            cleaned_text = extracted_text.strip()
            
            if len(cleaned_text) < 50:
                return f"Limited text extracted: {cleaned_text}"
            
            # Limit text length for API efficiency
            if len(cleaned_text) > 3000:
                cleaned_text = cleaned_text[:3000] + "... [text truncated]"
            
            return cleaned_text
            
        except Exception as e:
            return f"OCR extraction failed: {str(e)}"
    
    def classify_activity_from_text(self, extracted_text: str) -> Dict[str, Any]:
        """Classify the activity based on extracted text content"""
        
        # Create a comprehensive classification prompt for text analysis
        system_prompt = f"""Analyze this text content extracted from a user's screen via OCR and classify their current activity.

TEXT CONTENT FROM SCREEN:
{extracted_text}

Based on the text content above, classify the user's activity into ONE of these categories:
- PROGRAMMING: Code, programming languages, IDEs, GitHub, Stack Overflow, coding tutorials, development tools
- WEB_BROWSING: General web browsing, news sites, social media, entertainment websites
- GAMING: Video games, gaming websites, game launchers, gaming content
- PRODUCTIVITY: Documents, spreadsheets, presentations, email, calendar, office work, business apps
- MEDIA: Video streaming, music, entertainment content, YouTube, Netflix
- COMMUNICATION: Chat apps, messaging, video calls, meetings, social platforms for communication
- LEARNING: Educational content, tutorials, courses, documentation, research, learning platforms
- IDLE: Desktop, minimal content, screensaver, system interfaces
- OTHER: Unclear, mixed activities, or doesn't fit other categories

Look for specific keywords, application names, programming languages, code snippets, website names, etc.

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
            
            # Send the request
            response = requests.post(chat_url, headers=self.headers, json=payload)
            
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
    
    def analyze_current_activity(self) -> Dict[str, Any]:
        """Take screenshot, extract text, and classify activity"""
        print("📸 Taking screenshot...")
        
        screenshot_path = f"ocr_screenshot_{int(time.time())}.png"
        
        if not self.take_screenshot(screenshot_path):
            return {"success": False, "error": "Failed to take screenshot"}
        
        print("🔍 Extracting text from screenshot...")
        extracted_text = self.extract_text_from_screenshot(screenshot_path)
        
        if "failed" in extracted_text.lower():
            return {"success": False, "error": extracted_text}
        
        print(f"📝 Extracted {len(extracted_text)} characters of text")
        print(f"📄 Text preview: {extracted_text[:200]}...")
        
        print("🤖 Classifying activity with AnythingLLM...")
        result = self.classify_activity_from_text(extracted_text)
        
        # Clean up screenshot
        try:
            os.remove(screenshot_path)
        except:
            pass
        
        if result["success"]:
            result["extracted_text"] = extracted_text
        
        return result
    
    def monitor_activity(self, duration_seconds: int = 60, interval_seconds: int = 15):
        """Monitor user activity for a specified duration using OCR"""
        print(f"🔍 Starting OCR-based activity monitoring for {duration_seconds} seconds...")
        print(f"📸 Taking screenshots every {interval_seconds} seconds")
        print(f"📊 Screenshot method: {self.screenshot_method}")
        print(f"🔤 OCR available: {self.ocr_available}")
        print("-" * 60)
        
        if self.screenshot_method == "none":
            print("❌ Cannot monitor - no screenshot library available")
            return
        
        if not self.ocr_available:
            print("❌ Cannot monitor - OCR not available")
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
                        print(f"[{timestamp}] 🏆 Productive: {classification.get('is_productive', 'Unknown')}")
                        print(f"[{timestamp}] 🎯 Focus: {classification.get('focus_level', 'Unknown')}")
                        print(f"[{timestamp}] 📏 Text length: {result.get('extracted_text_length', 0)} chars")
                        
                        # Add to results
                        results.append({
                            "timestamp": timestamp,
                            "classification": classification,
                            "metrics": result.get("metrics", {}),
                            "text_length": result.get("extracted_text_length", 0)
                        })
                    else:
                        print(f"[{timestamp}] ❌ Classification parsing failed: {classification.get('error', 'Unknown error')}")
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
        print(f"\n📊 OCR MONITORING SUMMARY ({len(results)} samples)")
        print("=" * 60)
        
        if results:
            categories = {}
            total_confidence = 0
            productive_count = 0
            total_text_length = 0
            
            for result in results:
                classification = result["classification"]
                category = classification.get("category", "Unknown")
                confidence = classification.get("confidence", 0)
                is_productive = classification.get("is_productive", False)
                text_length = result.get("text_length", 0)
                
                categories[category] = categories.get(category, 0) + 1
                total_confidence += confidence
                total_text_length += text_length
                if is_productive:
                    productive_count += 1
            
            print("📈 Activity Distribution:")
            for category, count in sorted(categories.items()):
                percentage = (count / len(results)) * 100
                print(f"  {category}: {count} samples ({percentage:.1f}%)")
            
            print(f"\n🎯 Average Confidence: {total_confidence/len(results):.2f}")
            print(f"🏆 Productive Time: {productive_count}/{len(results)} samples ({(productive_count/len(results))*100:.1f}%)")
            print(f"📏 Average Text Length: {total_text_length/len(results):.0f} characters")
        else:
            print("❌ No successful classifications recorded")


def main():
    """Main function to run the OCR activity classifier"""
    classifier = OCRActivityClassifier()
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "monitor":
            # Monitor mode
            duration = int(sys.argv[2]) if len(sys.argv) > 2 else 60
            interval = int(sys.argv[3]) if len(sys.argv) > 3 else 15
            classifier.monitor_activity(duration, interval)
        elif sys.argv[1] == "text":
            # Test with provided text
            if len(sys.argv) > 2:
                test_text = " ".join(sys.argv[2:])
                result = classifier.classify_activity_from_text(test_text)
                if result["success"]:
                    classification = classifier.parse_classification_result(result["classification"])
                    print(f"\n📊 TEXT CLASSIFICATION RESULT:")
                    print("=" * 40)
                    print(json.dumps(classification, indent=2))
                else:
                    print(f"❌ Classification failed: {result['error']}")
            else:
                print("❌ Please provide text to classify")
        else:
            print("❌ Unknown command. Use 'monitor' or 'text'")
    else:
        # Default: single analysis
        print("🔤 Analyzing current screen activity with OCR...")
        result = classifier.analyze_current_activity()
        
        if result["success"]:
            classification = classifier.parse_classification_result(result["classification"])
            print(f"\n📊 CURRENT ACTIVITY (OCR-based):")
            print("=" * 40)
            if "error" not in classification:
                print(json.dumps(classification, indent=2))
                print(f"\n📏 Text extracted: {result.get('extracted_text_length', 0)} characters")
                print(f"⚡ Processing time: {result['metrics'].get('duration', 'Unknown')} seconds")
            else:
                print(f"❌ Classification parsing failed: {classification.get('error', 'Unknown error')}")
                if "raw_response" in classification:
                    print(f"📄 Raw response: {classification['raw_response'][:300]}...")
        else:
            print(f"❌ Analysis failed: {result['error']}")


if __name__ == "__main__":
    main() 
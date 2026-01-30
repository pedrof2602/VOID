"""
Test script for VOID Backend API
Tests the /input/voice endpoint with the existing temp_recording.wav file
"""

import requests
import os
from pathlib import Path

# Configuration
API_URL = "http://localhost:8000"
USER_ID = "98181061-0369-4267-9a9a-72f480744a2b"
AUDIO_FILE = "temp_recording.wav"

def test_health_check():
    """Test the health check endpoint"""
    print("\n🏥 Testing health check endpoint...")
    try:
        response = requests.get(f"{API_URL}/health", timeout=5)
        response.raise_for_status()
        data = response.json()
        print(f"✅ Health check passed: {data}")
        return True
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API. Is it running?")
        print("   Run: docker-compose up -d")
        return False
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

def test_voice_input():
    """Test the voice input endpoint"""
    print("\n🎤 Testing voice input endpoint...")
    
    # Check if audio file exists
    if not os.path.exists(AUDIO_FILE):
        print(f"❌ Audio file not found: {AUDIO_FILE}")
        print("   Please ensure temp_recording.wav exists in the backend directory")
        return False
    
    try:
        # Prepare the request
        files = {
            "file": ("recording.wav", open(AUDIO_FILE, "rb"), "audio/wav")
        }
        data = {
            "user_id": USER_ID
        }
        
        print(f"📤 Sending audio file: {AUDIO_FILE}")
        print(f"👤 User ID: {USER_ID}")
        
        # Send request
        response = requests.post(
            f"{API_URL}/input/voice",
            files=files,
            data=data,
            timeout=30  # STT + Brain processing can take time
        )
        
        response.raise_for_status()
        result = response.json()
        
        print(f"✅ Voice input processed successfully!")
        print(f"   Status: {result['status']}")
        print(f"   Message: {result['message']}")
        print(f"   Signal ID: {result.get('signal_id', 'N/A')}")
        print(f"   Signal Type: {result.get('signal_type', 'N/A')}")
        
        return True
        
    except requests.exceptions.Timeout:
        print("❌ Request timed out. Processing may take longer than expected.")
        return False
    except requests.exceptions.HTTPError as e:
        print(f"❌ HTTP Error: {e}")
        if hasattr(e.response, 'json'):
            try:
                error_detail = e.response.json()
                print(f"   Detail: {error_detail.get('detail', 'No details')}")
            except:
                pass
        return False
    except Exception as e:
        print(f"❌ Voice input test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("VOID Backend API - Test Suite")
    print("=" * 60)
    
    # Test 1: Health Check
    if not test_health_check():
        print("\n⚠️ Cannot proceed without a healthy API")
        return
    
    # Test 2: Voice Input
    test_voice_input()
    
    print("\n" + "=" * 60)
    print("Test suite completed!")
    print("=" * 60)
    print("\n📝 Next steps:")
    print("1. Check Supabase database for the inserted signal")
    print("2. Verify the signal payload structure")
    print("3. Test mobile polling integration")

if __name__ == "__main__":
    main()

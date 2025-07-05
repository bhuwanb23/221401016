#!/usr/bin/env python3
"""
Simple test to check authorization
"""

import requests
import json

def test_auth():
    """Test the authorization with the logging API."""
    
    # Authorization token
    auth_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJNYXBDbGFpbXMiOnsiYXVkIjoiaHR0cDovLzIwLjI0NC41Ni4xNDQvZXZhbHVhdGlvbi1zZXJ2aWNlIiwiZW1haWwiOiIyMjE0MDEwMTZAcmFqYWxha3NobWkuZWR1LmluIiwiZXhwIjoxNzUxNjkzOTE3LCJpYXQiOjE3NTE2OTMwMTcsImlzcyI6IkFmZm9yZCBNZWRpY2FsIFRlY2hub2xvZ2llcyBQcml2YXRlIExpbWl0ZWQiLCJqdGkiOiIxZDU4YmFlOC01NWM2LTQ4M2UtOTcwMy1lMDc1MWE5MmY2YzIiLCJsb2NhbGUiOiJlbi1JTiIsIm5hbWUiOiJiaHV3YW4gYiIsInN1YiI6ImZkNjNmNmI0LTkzNjYtNGVlZS1hMTk2LTM1OTFmNzE1MDkxOCJ9LCJlbWFpbCI6IjIyMTQwMTAxNkByYWphbGFrc2htaS5lZHUuaW4iLCJuYW1lIjoiYmh1d2FuIGIiLCJyb2xsTm8iOiIyMjE0MDEwMTYiLCJhY2Nlc3NDb2RlIjoiY1d5YVhXIiwiY2xpZW50SUQiOiJmZDYzZjZiNC05MzY2LTRlZWUtYTE5Ni0zNTkxZjcxNTA5MTgiLCJjbGllbnRTZWNyZXQiOiJRR05XWndyZXpFakRiWlFnIn0.Gb7oKr3iaABMhbn80I0HJkgMcrywbDgkovbi-awy6zQ"
    
    # API URL
    api_url = "http://20.244.56.144/evaluation-service/logs"
    
    # Test payload
    payload = {
        "stack": "backend",
        "level": "info",
        "package": "test",
        "message": "Authorization test"
    }
    
    # Headers with authorization
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {auth_token}'
    }
    
    print("🔐 Testing authorization...")
    print(f"📡 URL: {api_url}")
    print(f"📦 Payload: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(api_url, json=payload, headers=headers, timeout=10)
        
        print(f"📊 Status Code: {response.status_code}")
        print(f"📄 Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ Authorization successful!")
            return True
        else:
            print("❌ Authorization failed!")
            return False
            
    except Exception as e:
        print(f"❌ Request failed: {e}")
        return False

if __name__ == "__main__":
    success = test_auth()
    if success:
        print("\n🎉 Authorization test passed!")
    else:
        print("\n💥 Authorization test failed!") 
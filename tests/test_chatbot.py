#!/usr/bin/env python3
"""
Simple script to test the chatbot API.
This script sends a test message to the chatbot API and verifies the response.
"""

import os
import sys
import uuid
import json
import requests
from pathlib import Path
from dotenv import load_dotenv

def main():
    """Main function to test the chatbot API."""
    print("=== Chatbot API Test ===")
    
    # Load environment variables
    dotenv_path = Path(".env")
    if dotenv_path.exists():
        load_dotenv(dotenv_path=dotenv_path)
    else:
        print("Error: .env file not found.")
        sys.exit(1)
    
    # Get API key
    api_key = os.getenv("API_KEY")
    if not api_key:
        print("Error: API_KEY not set in .env file.")
        sys.exit(1)
    
    # Get API host and port
    api_host = os.getenv("API_HOST", "0.0.0.0")
    api_port = os.getenv("API_PORT", "8000")
    
    # Create API URL
    api_url = f"http://{api_host}:{api_port}/api/chat"
    
    # Create a unique session ID
    session_id = f"test-session-{uuid.uuid4()}"
    
    # Create request payload
    payload = {
        "message": "Hello, I need a website for my business",
        "session_id": session_id
    }
    
    # Create request headers
    headers = {
        "Content-Type": "application/json",
        "X-API-Key": api_key
    }
    
    print(f"Sending request to {api_url}...")
    print(f"Session ID: {session_id}")
    print(f"Message: {payload['message']}")
    
    try:
        # Send request
        response = requests.post(api_url, json=payload, headers=headers, timeout=10)
        
        # Check response
        if response.status_code == 200:
            data = response.json()
            print("\n✅ Success! Received response:")
            print(f"Response: {data['response']}")
            print(f"Session ID: {data['session_id']}")
            print(f"Conversation State: {data['conversation_state']['current_state']}")
            return True
        else:
            print(f"\n❌ Error: Received status code {response.status_code}")
            print(f"Response: {response.text}")
            return False
    
    except requests.exceptions.RequestException as e:
        print(f"\n❌ Error: {str(e)}")
        print("Please check if the server is running and try again.")
        return False

if __name__ == "__main__":
    main() 
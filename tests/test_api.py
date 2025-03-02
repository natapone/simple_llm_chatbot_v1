"""
Simple test script to demonstrate the API functionality.
"""

import os
import json
import asyncio
import uuid
from datetime import datetime

import httpx

# Set the API key
API_KEY = "test_api_key_123"
BASE_URL = "http://localhost:8000"

# Headers for API requests
headers = {
    "Content-Type": "application/json",
    "X-API-Key": API_KEY
}

async def test_chat_api():
    """Test the chat API functionality."""
    print("\n=== Testing Chat API ===")
    
    # Create a unique session ID
    session_id = f"test-session-{uuid.uuid4()}"
    
    # Send a message to the chatbot
    chat_url = f"{BASE_URL}/api/chat"
    chat_data = {
        "message": "I need a mobile app for my business",
        "session_id": session_id,
        "user_info": {
            "name": "Test User",
            "email": "test@example.com"
        }
    }
    
    async with httpx.AsyncClient() as client:
        # Send the chat request
        print(f"Sending chat request with session ID: {session_id}")
        response = await client.post(chat_url, headers=headers, json=chat_data)
        
        if response.status_code == 200:
            chat_response = response.json()
            print(f"Chat response: {chat_response['response']}")
            print(f"Conversation state: {json.dumps(chat_response['conversation_state'], indent=2)}")
        else:
            print(f"Error: {response.status_code} - {response.text}")
        
        # Get session info
        print("\nRetrieving session info")
        session_url = f"{BASE_URL}/api/sessions/{session_id}"
        response = await client.get(session_url, headers=headers)
        
        if response.status_code == 200:
            session_info = response.json()
            print(f"Session info: {json.dumps(session_info, indent=2)}")
        else:
            print(f"Error: {response.status_code} - {response.text}")
    
    return session_id

async def test_leads_api():
    """Test the leads API functionality."""
    print("\n=== Testing Leads API ===")
    
    # Create a test lead
    create_lead_url = f"{BASE_URL}/api/test/create-lead"
    
    async with httpx.AsyncClient() as client:
        # Create a test lead
        print("Creating test lead")
        response = await client.post(create_lead_url, headers=headers)
        
        if response.status_code == 200:
            lead = response.json()
            lead_id = lead["id"]
            print(f"Test lead created with ID: {lead_id}")
            print(f"Lead details: {json.dumps(lead, indent=2)}")
        else:
            print(f"Error: {response.status_code} - {response.text}")
            return
        
        # Get all leads
        print("\nRetrieving all leads")
        leads_url = f"{BASE_URL}/api/leads"
        response = await client.get(leads_url, headers=headers)
        
        if response.status_code == 200:
            leads = response.json()
            print(f"Total leads: {leads['total']}")
            print(f"Leads: {json.dumps(leads['leads'], indent=2)}")
        else:
            print(f"Error: {response.status_code} - {response.text}")
        
        # Update lead status
        print(f"\nUpdating lead status for {lead_id}")
        status_url = f"{BASE_URL}/api/leads/{lead_id}/status?status=completed"
        response = await client.put(status_url, headers=headers)
        
        if response.status_code == 200:
            status_response = response.json()
            print(f"Status update response: {json.dumps(status_response, indent=2)}")
        else:
            print(f"Error: {response.status_code} - {response.text}")
        
        # Get the updated lead
        print(f"\nRetrieving updated lead {lead_id}")
        lead_url = f"{BASE_URL}/api/leads/{lead_id}"
        response = await client.get(lead_url, headers=headers)
        
        if response.status_code == 200:
            updated_lead = response.json()
            print(f"Updated lead: {json.dumps(updated_lead, indent=2)}")
        else:
            print(f"Error: {response.status_code} - {response.text}")
    
    return lead_id

async def main():
    """Run all tests."""
    # Ensure we're in testing mode
    os.environ["TESTING"] = "True"
    
    # Test chat API
    session_id = await test_chat_api()
    
    # Test leads API
    lead_id = await test_leads_api()
    
    print("\n=== All tests completed successfully ===")
    print(f"Session ID: {session_id}")
    print(f"Lead ID: {lead_id}")

if __name__ == "__main__":
    asyncio.run(main()) 
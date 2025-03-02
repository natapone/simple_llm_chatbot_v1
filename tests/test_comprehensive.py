"""
Comprehensive test script for the chatbot application.
This script tests all aspects of the application including:
- Chat API with conversation flow
- Session management
- Lead creation and retrieval
- Error handling and edge cases
"""

import os
import json
import asyncio
import uuid
import time
from datetime import datetime
from typing import Dict, Any, List, Optional

import httpx
import pytest

# Configuration
API_KEY = "test_api_key_123"
BASE_URL = "http://localhost:8000"

# Headers for API requests
headers = {
    "Content-Type": "application/json",
    "X-API-Key": API_KEY
}

# Test data
test_user_info = {
    "name": "Sarah Johnson",
    "email": "sarah@sweetdelightsbakery.com"
}

# Conversation flow for bakery website project
bakery_conversation = [
    "I need a website for my bakery business",
    "I want a clean, minimalist design with warm colors that reflect our bakery's atmosphere",
    "The website will be for our customers to browse our products, place orders for pickup, and learn about our bakery through the blog",
    "We need the website completed within 2 months as we are planning a grand reopening of our bakery with expanded offerings",
    "Our budget for this project is around $5,000 to $8,000",
    "Yes, that summary is correct",
    f"My name is {test_user_info['name']} and you can reach me at {test_user_info['email']} or 555-123-4567"
]

class TestResult:
    """Class to track test results"""
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.total = 0
    
    def add_result(self, passed: bool, test_name: str):
        """Add a test result"""
        self.total += 1
        if passed:
            self.passed += 1
            print(f"✅ PASS: {test_name}")
        else:
            self.failed += 1
            print(f"❌ FAIL: {test_name}")
    
    def summary(self):
        """Print summary of test results"""
        print(f"\n=== Test Summary ===")
        print(f"Total tests: {self.total}")
        print(f"Passed: {self.passed}")
        print(f"Failed: {self.failed}")
        print(f"Success rate: {(self.passed / self.total) * 100:.1f}%")

# Initialize test results
results = TestResult()

async def test_health_endpoint():
    """Test the health check endpoint"""
    test_name = "Health endpoint"
    
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/health", headers=headers)
        
        if response.status_code == 200 and response.json().get("status") == "healthy":
            results.add_result(True, test_name)
        else:
            results.add_result(False, test_name)
            print(f"  Response: {response.status_code} - {response.text}")

async def test_conversation_flow():
    """Test a complete conversation flow from start to finish"""
    test_name = "Complete conversation flow"
    
    # Create a unique session ID
    session_id = f"test-bakery-{uuid.uuid4()}"
    print(f"\nTesting conversation flow with session ID: {session_id}")
    
    # Track conversation state
    current_state = None
    lead_created = False
    
    async with httpx.AsyncClient() as client:
        # Go through each message in the conversation
        for i, message in enumerate(bakery_conversation):
            print(f"\nStep {i+1}: Sending message: '{message[:50]}...' if len(message) > 50 else message")
            
            # Send the message
            chat_url = f"{BASE_URL}/api/chat"
            chat_data = {
                "message": message,
                "session_id": session_id
            }
            
            # Add user info on the last message
            if i == len(bakery_conversation) - 1:
                chat_data["user_info"] = test_user_info
            
            response = await client.post(chat_url, headers=headers, json=chat_data)
            
            if response.status_code == 200:
                chat_response = response.json()
                print(f"  Response: '{chat_response['response'][:100]}...' if len(chat_response['response']) > 100 else chat_response['response']")
                
                # Track the conversation state
                new_state = chat_response['conversation_state'].get('current_step')
                if new_state and new_state != current_state:
                    print(f"  State transition: {current_state} -> {new_state}")
                    current_state = new_state
                
                # Check if we've reached the handoff state (lead should be created)
                if current_state == "handoff":
                    lead_created = True
            else:
                print(f"  Error: {response.status_code} - {response.text}")
                results.add_result(False, test_name)
                return
        
        # Verify the conversation reached the handoff state
        if lead_created:
            results.add_result(True, test_name)
        else:
            results.add_result(False, f"{test_name} - Did not reach handoff state")
    
    return session_id

async def test_session_management():
    """Test session management functionality"""
    test_name = "Session management"
    
    # Create a unique session ID
    session_id = f"test-session-{uuid.uuid4()}"
    
    async with httpx.AsyncClient() as client:
        # 1. Create a new session with an initial message
        chat_url = f"{BASE_URL}/api/chat"
        chat_data = {
            "message": "Hello, I'm interested in a mobile app",
            "session_id": session_id
        }
        
        response = await client.post(chat_url, headers=headers, json=chat_data)
        if response.status_code != 200:
            results.add_result(False, f"{test_name} - Failed to create session")
            return
        
        # 2. Get session info
        session_url = f"{BASE_URL}/api/sessions/{session_id}"
        response = await client.get(session_url, headers=headers)
        
        if response.status_code == 200:
            session_info = response.json()
            if session_info.get("session_id") == session_id and len(session_info.get("conversation_history", [])) > 0:
                print(f"  Session created successfully with {len(session_info['conversation_history'])} messages")
            else:
                results.add_result(False, f"{test_name} - Session data incomplete")
                return
        else:
            results.add_result(False, f"{test_name} - Failed to retrieve session")
            return
        
        # 3. Add another message to the session
        chat_data = {
            "message": "I need it to have user authentication and payment processing",
            "session_id": session_id
        }
        
        response = await client.post(chat_url, headers=headers, json=chat_data)
        if response.status_code != 200:
            results.add_result(False, f"{test_name} - Failed to add message")
            return
        
        # 4. Verify the message was added
        response = await client.get(session_url, headers=headers)
        
        if response.status_code == 200:
            session_info = response.json()
            if len(session_info.get("conversation_history", [])) >= 4:  # 2 user messages + 2 assistant responses
                print(f"  Session updated successfully with {len(session_info['conversation_history'])} messages")
            else:
                results.add_result(False, f"{test_name} - Message not added to session")
                return
        else:
            results.add_result(False, f"{test_name} - Failed to retrieve updated session")
            return
        
        # 5. Delete the session
        response = await client.delete(session_url, headers=headers)
        
        if response.status_code == 200:
            print("  Session deleted successfully")
        else:
            results.add_result(False, f"{test_name} - Failed to delete session")
            return
        
        # 6. Verify the session was deleted
        response = await client.get(session_url, headers=headers)
        
        if response.status_code == 404:
            print("  Session deletion verified")
            results.add_result(True, test_name)
        else:
            results.add_result(False, f"{test_name} - Session not deleted")

async def test_lead_management():
    """Test lead management functionality"""
    test_name = "Lead management"
    
    async with httpx.AsyncClient() as client:
        # 1. Create a test lead
        create_lead_url = f"{BASE_URL}/api/test/create-lead"
        
        response = await client.post(create_lead_url, headers=headers)
        
        if response.status_code == 200:
            lead = response.json()
            lead_id = lead["id"]
            print(f"  Test lead created with ID: {lead_id}")
        else:
            results.add_result(False, f"{test_name} - Failed to create test lead")
            return
        
        # 2. Get all leads and verify the new lead is included
        leads_url = f"{BASE_URL}/api/leads"
        response = await client.get(leads_url, headers=headers)
        
        if response.status_code == 200:
            leads = response.json()
            lead_ids = [lead["id"] for lead in leads.get("leads", [])]
            
            if lead_id in lead_ids:
                print(f"  Lead found in leads list")
            else:
                results.add_result(False, f"{test_name} - Lead not found in leads list")
                return
        else:
            results.add_result(False, f"{test_name} - Failed to retrieve leads")
            return
        
        # 3. Test pagination
        leads_url = f"{BASE_URL}/api/leads?limit=1&offset=0"
        response = await client.get(leads_url, headers=headers)
        
        if response.status_code == 200:
            leads = response.json()
            if len(leads.get("leads", [])) == 1 and leads.get("total", 0) > 1:
                print(f"  Pagination working correctly")
            else:
                results.add_result(False, f"{test_name} - Pagination not working correctly")
                return
        else:
            results.add_result(False, f"{test_name} - Failed to test pagination")
            return
        
        # 4. Update lead status
        status_url = f"{BASE_URL}/api/leads/{lead_id}/status?status=in_progress"
        response = await client.put(status_url, headers=headers)
        
        if response.status_code == 200:
            print(f"  Lead status updated to 'in_progress'")
        else:
            results.add_result(False, f"{test_name} - Failed to update lead status")
            return
        
        # 5. Verify the status was updated
        lead_url = f"{BASE_URL}/api/leads/{lead_id}"
        response = await client.get(lead_url, headers=headers)
        
        if response.status_code == 200:
            updated_lead = response.json()
            if updated_lead.get("follow_up_status") == "in_progress":
                print(f"  Lead status update verified")
                results.add_result(True, test_name)
            else:
                results.add_result(False, f"{test_name} - Lead status not updated")
        else:
            results.add_result(False, f"{test_name} - Failed to retrieve updated lead")

async def test_error_handling():
    """Test error handling in the API"""
    test_name = "Error handling"
    errors_handled_correctly = True
    
    async with httpx.AsyncClient() as client:
        # 1. Test invalid API key
        invalid_headers = headers.copy()
        invalid_headers["X-API-Key"] = "invalid_key"
        
        response = await client.get(f"{BASE_URL}/api/leads", headers=invalid_headers)
        
        if response.status_code == 401:
            print("  Invalid API key handled correctly")
        else:
            print(f"  Error: Invalid API key returned {response.status_code} instead of 401")
            errors_handled_correctly = False
        
        # 2. Test non-existent session
        session_url = f"{BASE_URL}/api/sessions/non-existent-session"
        response = await client.get(session_url, headers=headers)
        
        if response.status_code == 404:
            print("  Non-existent session handled correctly")
        else:
            print(f"  Error: Non-existent session returned {response.status_code} instead of 404")
            errors_handled_correctly = False
        
        # 3. Test non-existent lead
        lead_url = f"{BASE_URL}/api/leads/non-existent-lead"
        response = await client.get(lead_url, headers=headers)
        
        if response.status_code == 404:
            print("  Non-existent lead handled correctly")
        else:
            print(f"  Error: Non-existent lead returned {response.status_code} instead of 404")
            errors_handled_correctly = False
        
        # 4. Test invalid lead status update
        status_url = f"{BASE_URL}/api/leads/non-existent-lead/status?status=completed"
        response = await client.put(status_url, headers=headers)
        
        if response.status_code == 404:
            print("  Invalid lead status update handled correctly")
        else:
            print(f"  Error: Invalid lead status update returned {response.status_code} instead of 404")
            errors_handled_correctly = False
        
        results.add_result(errors_handled_correctly, test_name)

async def main():
    """Run all tests"""
    # Ensure we're in testing mode
    os.environ["TESTING"] = "True"
    
    print("\n=== Starting Comprehensive Tests ===")
    print("Make sure the server is running with TESTING=True in the .env file")
    
    # Test health endpoint
    print("\n--- Testing Health Endpoint ---")
    await test_health_endpoint()
    
    # Test conversation flow
    print("\n--- Testing Conversation Flow ---")
    session_id = await test_conversation_flow()
    
    # Test session management
    print("\n--- Testing Session Management ---")
    await test_session_management()
    
    # Test lead management
    print("\n--- Testing Lead Management ---")
    await test_lead_management()
    
    # Test error handling
    print("\n--- Testing Error Handling ---")
    await test_error_handling()
    
    # Print test summary
    results.summary()
    
    if results.failed == 0:
        print("\n🎉 All tests passed successfully! 🎉")
    else:
        print(f"\n⚠️ {results.failed} tests failed. Please check the output above for details.")

if __name__ == "__main__":
    asyncio.run(main()) 
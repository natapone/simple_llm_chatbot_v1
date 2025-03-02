"""
Performance and reliability test script for the chatbot API.
This script tests the API's performance under load and its reliability over time.
"""

import os
import json
import asyncio
import uuid
import time
from datetime import datetime
from typing import List, Dict, Any
import statistics

import httpx

# Configuration
API_KEY = "test_api_key_123"
BASE_URL = "http://localhost:8000"

# Headers for API requests
headers = {
    "Content-Type": "application/json",
    "X-API-Key": API_KEY
}

class PerformanceMetrics:
    """Class to track performance metrics"""
    def __init__(self):
        self.response_times = []
        self.success_count = 0
        self.error_count = 0
        self.start_time = None
        self.end_time = None
    
    def start(self):
        """Start the performance test"""
        self.start_time = time.time()
    
    def end(self):
        """End the performance test"""
        self.end_time = time.time()
    
    def add_result(self, response_time: float, success: bool):
        """Add a test result"""
        self.response_times.append(response_time)
        if success:
            self.success_count += 1
        else:
            self.error_count += 1
    
    def summary(self):
        """Print summary of performance metrics"""
        total_requests = self.success_count + self.error_count
        duration = self.end_time - self.start_time
        
        print("\n=== Performance Test Summary ===")
        print(f"Total requests: {total_requests}")
        print(f"Successful requests: {self.success_count}")
        print(f"Failed requests: {self.error_count}")
        print(f"Success rate: {(self.success_count / total_requests) * 100:.1f}%")
        print(f"Total duration: {duration:.2f} seconds")
        print(f"Requests per second: {total_requests / duration:.2f}")
        
        if self.response_times:
            print("\nResponse time statistics (seconds):")
            print(f"  Min: {min(self.response_times):.4f}")
            print(f"  Max: {max(self.response_times):.4f}")
            print(f"  Mean: {statistics.mean(self.response_times):.4f}")
            print(f"  Median: {statistics.median(self.response_times):.4f}")
            if len(self.response_times) > 1:
                print(f"  Std Dev: {statistics.stdev(self.response_times):.4f}")
            
            # Calculate percentiles
            sorted_times = sorted(self.response_times)
            p90_index = int(len(sorted_times) * 0.9)
            p95_index = int(len(sorted_times) * 0.95)
            p99_index = int(len(sorted_times) * 0.99)
            
            print(f"  90th percentile: {sorted_times[p90_index]:.4f}")
            print(f"  95th percentile: {sorted_times[p95_index]:.4f}")
            if p99_index < len(sorted_times):
                print(f"  99th percentile: {sorted_times[p99_index]:.4f}")

async def test_chat_endpoint_performance(num_requests: int = 20, concurrency: int = 3):
    """Test the performance of the chat endpoint under load"""
    print(f"\n=== Testing Chat Endpoint Performance ===")
    print(f"Sending {num_requests} requests with concurrency of {concurrency}")
    
    metrics = PerformanceMetrics()
    metrics.start()
    
    # Create a semaphore to limit concurrency
    semaphore = asyncio.Semaphore(concurrency)
    
    async def send_request(request_id: int):
        """Send a single request to the chat endpoint"""
        session_id = f"perf-test-{uuid.uuid4()}"
        message = "I need a website for my business"
        
        chat_data = {
            "message": message,
            "session_id": session_id
        }
        
        async with semaphore:
            start_time = time.time()
            success = False
            
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        f"{BASE_URL}/api/chat",
                        headers=headers,
                        json=chat_data,
                        timeout=5.0  # Reduced timeout for testing
                    )
                    
                    end_time = time.time()
                    response_time = end_time - start_time
                    
                    if response.status_code == 200:
                        success = True
                    else:
                        print(f"Request {request_id} failed with status code {response.status_code}")
            
            except Exception as e:
                end_time = time.time()
                response_time = end_time - start_time
                print(f"Request {request_id} failed with exception: {str(e)}")
            
            metrics.add_result(response_time, success)
            
            if request_id % 5 == 0:
                print(f"Completed {request_id} requests...")
    
    # Create tasks for all requests
    tasks = [send_request(i) for i in range(1, num_requests + 1)]
    
    # Run all tasks concurrently
    await asyncio.gather(*tasks)
    
    metrics.end()
    metrics.summary()
    
    return metrics

async def test_api_reliability(duration_seconds: int = 10, request_interval: float = 1.0):
    """Test the reliability of the API over time"""
    print(f"\n=== Testing API Reliability ===")
    print(f"Running for {duration_seconds} seconds with {request_interval} second intervals")
    
    metrics = PerformanceMetrics()
    metrics.start()
    
    # Create a unique session ID for this test
    session_id = f"reliability-test-{uuid.uuid4()}"
    
    # Messages to send in sequence
    messages = [
        "I need a website for my business",
        "It should have a modern design with a blog",
        "It's for a consulting business",
        "We need it within 3 months",
        "Our budget is around $10,000"
    ]
    
    start_time = time.time()
    message_index = 0
    request_count = 0
    
    while time.time() - start_time < duration_seconds:
        message = messages[message_index % len(messages)]
        message_index += 1
        
        chat_data = {
            "message": message,
            "session_id": session_id
        }
        
        request_start = time.time()
        success = False
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{BASE_URL}/api/chat",
                    headers=headers,
                    json=chat_data,
                    timeout=5.0  # Reduced timeout for testing
                )
                
                request_end = time.time()
                response_time = request_end - request_start
                
                if response.status_code == 200:
                    success = True
                else:
                    print(f"Request {request_count} failed with status code {response.status_code}")
        
        except Exception as e:
            request_end = time.time()
            response_time = request_end - request_start
            print(f"Request {request_count} failed with exception: {str(e)}")
        
        metrics.add_result(response_time, success)
        request_count += 1
        
        if request_count % 5 == 0:
            print(f"Completed {request_count} requests over {time.time() - start_time:.1f} seconds...")
        
        # Wait for the next interval
        await asyncio.sleep(request_interval)
    
    metrics.end()
    
    print(f"\nReliability test completed with {request_count} requests over {metrics.end_time - metrics.start_time:.1f} seconds")
    metrics.summary()
    
    return metrics

async def test_endpoint_availability():
    """Test the availability of all API endpoints"""
    print("\n=== Testing API Endpoint Availability ===")
    
    endpoints = [
        {"method": "GET", "url": "/"},
        {"method": "GET", "url": "/health"},
        {"method": "GET", "url": "/api/leads"},
        {"method": "POST", "url": "/api/chat", "data": {"message": "Hello", "session_id": f"test-{uuid.uuid4()}"}}
    ]
    
    results = {}
    
    async with httpx.AsyncClient() as client:
        for endpoint in endpoints:
            method = endpoint["method"]
            url = f"{BASE_URL}{endpoint['url']}"
            data = endpoint.get("data")
            
            print(f"Testing {method} {url}")
            
            try:
                if method == "GET":
                    response = await client.get(url, headers=headers, timeout=5.0)
                elif method == "POST":
                    response = await client.post(url, headers=headers, json=data, timeout=5.0)
                
                results[endpoint["url"]] = {
                    "status_code": response.status_code,
                    "available": response.status_code < 500
                }
                
                print(f"  Status: {response.status_code}")
            
            except Exception as e:
                results[endpoint["url"]] = {
                    "status_code": None,
                    "available": False,
                    "error": str(e)
                }
                
                print(f"  Error: {str(e)}")
    
    # Print summary
    print("\nEndpoint Availability Summary:")
    available_count = sum(1 for result in results.values() if result["available"])
    
    for url, result in results.items():
        status = "✅ Available" if result["available"] else "❌ Unavailable"
        print(f"{status}: {url}")
    
    print(f"\nAvailable endpoints: {available_count}/{len(endpoints)} ({available_count/len(endpoints)*100:.1f}%)")
    
    return results

async def main():
    """Run all performance tests"""
    # Ensure we're in testing mode
    os.environ["TESTING"] = "True"
    
    print("\n=== Starting Performance and Reliability Tests ===")
    print("Make sure the server is running with TESTING=True in the .env file")
    
    # Test endpoint availability
    await test_endpoint_availability()
    
    # Test chat endpoint performance
    # Parameters: number of requests, concurrency level
    await test_chat_endpoint_performance()
    
    # Test API reliability
    # Parameters: duration in seconds, request interval in seconds
    await test_api_reliability()
    
    print("\n=== All Performance and Reliability Tests Completed ===")

if __name__ == "__main__":
    asyncio.run(main()) 
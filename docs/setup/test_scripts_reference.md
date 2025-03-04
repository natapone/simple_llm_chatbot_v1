# Test Scripts Reference

This document provides detailed information about the test scripts available in the chatbot application.

## Overview

The application includes several test scripts designed to validate different aspects of the system. These scripts can be run individually or together using the test runner.

## Test Runner

The test runner script (`tests/run_all_tests.py`) provides a convenient way to run all tests or specific test scripts:

```bash
# Run all tests
python -m tests.run_all_tests

# Run a specific test
python -m tests.run_all_tests --test test_api.py

# Run tests with verbose output
python -m tests.run_all_tests --verbose

# Run tests without starting the server (if it's already running)
python -m tests.run_all_tests --no-server
```

The test runner handles:
- Starting the server in testing mode
- Waiting for the server to be fully initialized
- Running the specified tests
- Properly shutting down the server after tests complete
- Providing a summary of test results

## Test Scripts by Category

### API Tests

#### Basic API Tests (`tests/test_api.py`)

This script tests the basic API functionality of the application:

- **Health Check**: Verifies that the server is running and responding to requests
- **Chat API**: Tests the chat endpoint with a simple message
- **Leads API**: Tests the leads endpoint to ensure it returns the expected data
- **End-to-End Test**: Simulates a simple conversation and verifies that a lead is created

Example:
```bash
python -m tests.test_api
```

#### Simple Chatbot API Test (`tests/test_chatbot.py`)

This script provides a simple test of the chatbot API:

- **API Connection**: Tests the connection to the API
- **Chat Endpoint**: Sends a test message and verifies the response
- **Session Management**: Verifies that a session ID is created and maintained

Example:
```bash
python -m tests.test_chatbot
```

### Functional Tests

#### Comprehensive Tests (`tests/test_comprehensive.py`)

This script provides comprehensive testing of all aspects of the application:

- **Health Endpoint**: Tests the health endpoint for server status
- **Conversation Flow**: Tests the complete conversation flow from start to finish
- **Session Management**: Tests session creation, retrieval, and deletion
- **Lead Management**: Tests lead creation, retrieval, and updating
- **Error Handling**: Tests error responses for invalid inputs and unauthorized access

Example:
```bash
python -m tests.test_comprehensive
```

#### Conversation Scenario Tests (`tests/test_conversation_scenarios.py`)

This script tests different conversation scenarios to ensure the chatbot can handle various client requests:

- **Website Project**: Tests a conversation about a website project
- **Mobile App Project**: Tests a conversation about a mobile app project
- **E-commerce Project**: Tests a conversation about an e-commerce project
- **Chatbot Project**: Tests a conversation about a chatbot project
- **Conversation with Interruption**: Tests the chatbot's ability to handle topic changes
- **Conversation with Minimal Information**: Tests the chatbot's ability to handle minimal input

Example:
```bash
python -m tests.test_conversation_scenarios
```

### Storage Tests

#### CSV Storage Tests (`tests/test_csv_storage.py`)

This script tests the CSV storage functionality:

- **Lead Storage**: Tests storing a lead in the CSV file
- **Lead Retrieval**: Tests retrieving a lead from the CSV file
- **Data Integrity**: Verifies that the stored data matches the original data

Example:
```bash
python -m tests.test_csv_storage
```

### Performance Tests

#### API Performance Tests (`tests/test_performance.py`)

This script tests the performance and reliability of the API:

- **Endpoint Availability**: Tests that all endpoints are available
- **Chat Endpoint Performance**: Tests the performance of the chat endpoint under load
  - Default: 20 requests with concurrency of 3
  - Configurable parameters for number of requests and concurrency level
- **API Reliability**: Tests the reliability of the API over time
  - Default: 10 seconds with 1.0-second intervals
  - Configurable parameters for duration and request interval

Example:
```bash
python -m tests.test_performance
```

## Writing New Tests

When writing new tests, follow these guidelines:

1. **Use the Testing Mode**: Ensure that the tests work with the mock services by setting `TESTING=True`
2. **Create Unique Session IDs**: Use unique session IDs for each test to avoid conflicts
3. **Clean Up After Tests**: Delete any test data created during the test
4. **Handle Errors Gracefully**: Catch and report errors properly
5. **Provide Detailed Output**: Include enough information to diagnose failures

Example of creating a new test:

```python
async def test_new_feature():
    """Test a new feature of the application"""
    print("\n=== Testing New Feature ===")
    
    # Create a unique session ID
    session_id = f"test-new-feature-{uuid.uuid4()}"
    
    # Test code here...
    
    # Return True if the test passed, False otherwise
    return True
```

## Troubleshooting

If you encounter issues with the tests:

1. **Server Not Starting**: Check that the port is not already in use
2. **Connection Errors**: Ensure the server is running and accessible
3. **Test Failures**: Check the error messages and server logs for details
4. **Timeout Errors**: Increase the timeout values for slow operations

For more information, see the [Testing Guide](testing_guide.md). 
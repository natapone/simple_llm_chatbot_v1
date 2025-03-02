# Testing Guide

## Overview

This document provides instructions for testing the chatbot application without relying on external services like OpenAI and Google Sheets. The application includes a testing mode that uses mock implementations of these services.

## Enabling Testing Mode

Testing mode is controlled by the `TESTING` environment variable. When set to `True`, the application will use mock implementations for:

- LLM service (instead of calling OpenAI)
- Google Sheets service (instead of accessing actual Google Sheets)

To enable testing mode, set the following in your `.env` file:

```
TESTING=True
```

## Mock Implementations

### Mock LLM Service

When in testing mode, the LLM service will:

- Return predefined mock responses instead of calling OpenAI
- Simulate entity extraction with mock data
- Provide mock conversation summaries

This allows testing the conversation flow without consuming OpenAI API credits or requiring an internet connection.

### Mock Google Sheets Service

The mock Google Sheets service:

- Stores leads in memory instead of in Google Sheets
- Provides pagination and filtering for lead retrieval
- Supports all CRUD operations on leads
- Simulates errors and retries

## Running Tests

### Test Runner

The project includes a test runner script that can run all tests or specific test scripts. The test runner will automatically start and stop the server for you, ensuring a clean testing environment:

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

### Available Test Scripts

The project includes several test scripts for different aspects of the application:

1. **Basic API Tests** (`test_api.py`):
   - Tests basic API functionality
   - Verifies chat API and leads API endpoints
   - Simple end-to-end test of the main features

2. **Comprehensive Tests** (`test_comprehensive.py`):
   - Tests all aspects of the application
   - Includes health endpoint, conversation flow, session management, lead management, and error handling
   - Provides detailed test results and summary

3. **Conversation Scenario Tests** (`test_conversation_scenarios.py`):
   - Tests different conversation scenarios (website, mobile app, e-commerce, chatbot)
   - Tests handling of topic changes and minimal information
   - Verifies that leads are created correctly for each scenario

4. **Performance Tests** (`test_performance.py`):
   - Tests API performance under load
   - Tests API reliability over time
   - Tests endpoint availability
   - Provides detailed performance metrics

For detailed information about each test script, see the [Test Scripts Reference](test_scripts_reference.md).

### Manual Testing

You can manually test the API endpoints using tools like `curl` or Postman. Make sure to include the API key in your requests:

```bash
curl http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your_api_key_here" \
  -d '{"message": "Hello", "session_id": "test-session-123"}'
```

## Test Endpoints

In testing mode, additional endpoints are available:

- `POST /api/test/create-lead`: Creates a test lead with sample data

## Troubleshooting

If you encounter issues with the tests:

1. Ensure the server is running in testing mode
2. Check that the API key in your test matches the one in your `.env` file
3. Verify that the server is accessible at the expected URL
4. Check the server logs for any error messages
5. If the server fails to start, check the error output from the test runner

## Adding New Tests

When adding new functionality to the application, consider:

1. Updating the mock implementations to support the new features
2. Adding test cases to the test script
3. Creating unit tests for individual components
4. Documenting the testing approach for the new features

## Performance Testing Considerations

When running performance tests:

1. Ensure the server has sufficient resources
2. Start with a small number of requests and gradually increase
3. Monitor server logs for errors or performance issues
4. Consider the impact of mock services on performance results

## Continuous Integration

For continuous integration environments:

1. Set `TESTING=True` in the CI environment
2. Run the test runner with appropriate flags
3. Use the exit code to determine test success or failure
4. Capture test output for debugging failed tests 
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

### Manual Testing

You can manually test the API endpoints using tools like `curl` or Postman. Make sure to include the API key in your requests:

```bash
curl http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your_api_key_here" \
  -d '{"message": "Hello", "session_id": "test-session-123"}'
```

### Automated Testing

The project includes a test script that verifies all key functionality:

```bash
# Make sure the server is running first
python -m app.main &

# Then run the test script
python -m tests.test_api
```

The test script checks:

1. Chat API functionality
   - Creating sessions
   - Sending messages
   - Retrieving session information

2. Leads API functionality
   - Creating leads
   - Retrieving leads with pagination
   - Updating lead status
   - Retrieving specific leads

## Test Endpoints

In testing mode, additional endpoints are available:

- `POST /api/test/create-lead`: Creates a test lead with sample data

## Troubleshooting

If you encounter issues with the tests:

1. Ensure the server is running in testing mode
2. Check that the API key in your test matches the one in your `.env` file
3. Verify that the server is accessible at the expected URL
4. Check the server logs for any error messages

## Adding New Tests

When adding new functionality to the application, consider:

1. Updating the mock implementations to support the new features
2. Adding test cases to the test script
3. Creating unit tests for individual components
4. Documenting the testing approach for the new features 
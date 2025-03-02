# API Reference

This document provides detailed information about the API endpoints available in the chatbot system.

## Base URL

```
http://localhost:8000
```

## Authentication

All API endpoints require authentication using an API key. Include the API key in the request header:

```
X-API-Key: your_api_key_here
```

## Endpoints

### Chat Endpoint

#### `POST /api/chat`

Send a message to the chatbot and receive a response.

**Request Body:**

```json
{
  "message": "I need a mobile app for my business",
  "session_id": "unique_session_identifier",
  "user_info": {
    "name": "Optional User Name",
    "email": "optional_email@example.com"
  }
}
```

**Response:**

```json
{
  "response": "That sounds interesting! Could you describe the key features or functionalities you have in mind for your mobile app?",
  "session_id": "unique_session_identifier",
  "conversation_state": {
    "current_step": "requirement_gathering",
    "collected_info": {
      "project_type": "mobile_app"
    }
  }
}
```

**Status Codes:**

- `200 OK`: Request successful
- `400 Bad Request`: Invalid request format
- `401 Unauthorized`: Invalid or missing API key
- `500 Internal Server Error`: Server error

### Session Management

#### `GET /api/sessions/{session_id}`

Retrieve information about a specific chat session.

**Response:**

```json
{
  "session_id": "unique_session_identifier",
  "created_at": "2023-07-01T12:00:00Z",
  "last_active": "2023-07-01T12:05:00Z",
  "conversation_history": [
    {
      "role": "user",
      "content": "I need a mobile app for my business",
      "timestamp": "2023-07-01T12:00:00Z"
    },
    {
      "role": "assistant",
      "content": "That sounds interesting! Could you describe the key features or functionalities you have in mind for your mobile app?",
      "timestamp": "2023-07-01T12:00:05Z"
    }
  ],
  "collected_info": {
    "project_type": "mobile_app"
  }
}
```

#### `DELETE /api/sessions/{session_id}`

Delete a specific chat session.

**Response:**

```json
{
  "status": "success",
  "message": "Session deleted successfully"
}
```

### Lead Management

#### `GET /api/leads`

Retrieve a list of leads collected by the chatbot.

**Query Parameters:**

- `limit` (optional): Maximum number of leads to return (default: 10)
- `offset` (optional): Number of leads to skip (default: 0)
- `sort_by` (optional): Field to sort by (default: "created_at")
- `sort_order` (optional): Sort order, either "asc" or "desc" (default: "desc")

**Response:**

```json
{
  "total": 100,
  "limit": 10,
  "offset": 0,
  "leads": [
    {
      "id": "lead_123",
      "client_name": "John Doe",
      "contact_info": "john@example.com",
      "project_type": "mobile_app",
      "requirements_summary": "A mobile app with payment integration and user authentication",
      "timeline": "3 months",
      "budget_range": "$10,000-$20,000",
      "follow_up_status": "pending",
      "created_at": "2023-07-01T12:30:00Z"
    },
    // More leads...
  ]
}
```

#### `GET /api/leads/{lead_id}`

Retrieve information about a specific lead.

**Response:**

```json
{
  "id": "lead_123",
  "client_name": "John Doe",
  "contact_info": "john@example.com",
  "project_type": "mobile_app",
  "requirements_summary": "A mobile app with payment integration and user authentication",
  "timeline": "3 months",
  "budget_range": "$10,000-$20,000",
  "follow_up_status": "pending",
  "created_at": "2023-07-01T12:30:00Z",
  "conversation_history": [
    // Full conversation history
  ]
}
```

### Webhook Integration

#### `POST /api/webhook`

Register a webhook to receive notifications about new leads.

**Request Body:**

```json
{
  "url": "https://your-service.com/webhook",
  "events": ["new_lead", "lead_updated"],
  "secret": "your_webhook_secret"
}
```

**Response:**

```json
{
  "webhook_id": "webhook_123",
  "status": "active",
  "message": "Webhook registered successfully"
}
```

## Error Responses

All endpoints return errors in the following format:

```json
{
  "error": {
    "code": "error_code",
    "message": "Human-readable error message",
    "details": {
      // Additional error details if available
    }
  }
}
```

## Rate Limiting

API requests are rate-limited to 100 requests per minute per API key. If you exceed this limit, you'll receive a `429 Too Many Requests` response with a `Retry-After` header indicating when you can resume making requests.

## Versioning

The API version is specified in the URL path:

```
/api/v1/chat
```

The current version is v1. When new versions are released, the previous versions will remain available for a deprecation period. 
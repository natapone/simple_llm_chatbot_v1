# LiteLLM + Langflow Chatbot System Design

## 1. Project Overview

This document outlines the system design for a lightweight chatbot using LiteLLM and Langflow. The chatbot will function as a pre-sales assistant for a software development company, focusing on:

- Understanding client needs (requirement gathering)
- Extracting key information (use case, expectations, timeline)
- Indirectly assessing budget
- Summarizing client requests
- Collecting contact details
- Storing lead information in Google Sheets

## 2. System Architecture

### 2.1 Core Components

| Component | Description |
|-----------|------------|
| **LiteLLM** | Manages the connection to OpenAI for NLU and response generation using GPT-4o-mini model |
| **Langflow** | Provides a graph-based conversation flow editor to structure chatbot logic |
| **Google Sheets API** | Stores client information and lead data for follow-ups |
| **FastAPI Backend** | Handles requests from Langflow to interact with external APIs (Google Sheets) |

### 2.2 Component Interactions

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   User      │────▶│  FastAPI    │────▶│  Langflow   │
│  Interface  │◀────│  Backend    │◀────│  Flow Logic │
└─────────────┘     └─────────────┘     └─────────────┘
                          │                    │
                          ▼                    ▼
                    ┌─────────────┐     ┌─────────────┐
                    │Google Sheets│     │   LiteLLM   │
                    │     API     │     │  (GPT-4o-mini) │
                    └─────────────┘     └─────────────┘
```

## 3. Technical Specifications

### 3.1 LiteLLM Configuration

- **Model**: GPT-4o-mini
- **API Version**: Latest OpenAI API (v1.12.0+)
- **Context Management**: Maintaining conversation history for contextual responses
- **Temperature Setting**: 0.7 (balanced between creativity and consistency)
- **Python Version**: 3.11+

### 3.2 Langflow Implementation

- **Flow Design**: Visual graph-based conversation flow
- **Node Types**:
  - Input Processing Nodes
  - Intent Classification Nodes
  - Entity Extraction Nodes
  - Response Generation Nodes
  - Data Storage Nodes

### 3.3 FastAPI Backend

- **Endpoints**:
  - `/chat`: Main chat interaction endpoint
  - `/webhook`: For potential external integrations
  - `/admin`: Administrative functions (protected)
- **Middleware**:
  - Authentication
  - Rate Limiting
  - Logging
  - CORS

### 3.4 Google Sheets Integration

- **Data Structure**:
  - Timestamp
  - Client Name
  - Contact Information
  - Project Type
  - Requirements Summary
  - Timeline
  - Budget Range
  - Follow-up Status

## 4. Security Considerations

### 4.1 API Security

- API keys stored securely in environment variables
- Rate limiting to prevent abuse
- Input validation to prevent injection attacks
- CORS configuration to restrict origins

### 4.2 Data Protection

- Encryption for sensitive data
- Secure credential storage
- Data anonymization where appropriate
- Regular security audits

## 5. Implementation Phases

### Phase 1: Foundation Setup (Week 1-2)
- Project structure setup
- Environment configuration
- Basic FastAPI server
- LiteLLM integration with GPT-4o-mini
- Logging system

### Phase 2: Core Features (Week 3-4)
- Conversation flow implementation in Langflow
- Response generation system
- Basic data validation

### Phase 3: Integration & Storage (Week 5-6)
- Google Sheets API integration
- Lead data management
- Error recovery mechanisms

### Phase 4: Testing & Deployment (Week 7-8)
- Unit and integration testing
- Performance optimization
- Documentation completion
- Deployment preparation

## 6. Monitoring & Maintenance

### 6.1 Logging Strategy

- Request/response logging
- Error tracking
- Performance metrics
- User interaction history

### 6.2 Maintenance Plan

- Weekly review of conversation logs
- Monthly model performance evaluation
- Quarterly security review
- Continuous improvement based on user feedback

## 7. Future Enhancements

- WhatsApp & LINE Integration
- Automated appointment scheduling
- CRM integration (HubSpot, Salesforce)
- Multilingual support
- Advanced analytics dashboard 

## 8. Testing Framework

### 8.1 Testing Architecture

The application includes a comprehensive testing framework designed to validate all aspects of the system without relying on external services:

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  Test       │────▶│  Test       │────▶│  Mock       │
│  Runner     │◀────│  Scripts    │◀────│  Services   │
└─────────────┘     └─────────────┘     └─────────────┘
       │                   │                   │
       │                   │                   │
       ▼                   ▼                   ▼
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  Server     │────▶│  API        │────▶│  Core       │
│  Management │◀────│  Endpoints  │◀────│  Logic      │
└─────────────┘     └─────────────┘     └─────────────┘
```

### 8.2 Mock Services

- **Mock LLM Service**: Simulates responses from the LLM without calling OpenAI
- **Mock Google Sheets Service**: Stores data in memory instead of in Google Sheets

### 8.3 Test Scripts

- **Basic API Tests**: Validates core API functionality
- **Comprehensive Tests**: Tests all aspects of the application
- **Conversation Scenario Tests**: Tests different conversation scenarios
- **Performance Tests**: Tests API performance and reliability

### 8.4 Test Runner

The test runner script provides:
- Automatic server startup and shutdown
- Support for running specific tests
- Detailed test results and summary
- Proper error handling and reporting 
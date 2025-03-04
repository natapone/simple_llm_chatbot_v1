# Simple LLM Chatbot

## Overview

This project implements a lightweight chatbot using LiteLLM and Langflow. The chatbot functions as a pre-sales assistant for a software development company, designed to understand client needs, extract key information about their project needs, and store lead data in CSV files for follow-up.

## Features

- **Conversational Interface**: Natural language interaction with potential clients
- **Lead Information Extraction**: Automatically identifies and extracts key details:
  - Client name and contact information
  - Project requirements and scope
  - Timeline expectations
  - Budget range (indirectly assessed)
- **Data Storage**: Stores lead information in CSV files for easy access and management
- **Testing Mode**: Includes a testing mode that uses mock implementations of external services

## Project Structure

```
simple_llm_chatbot/
├── app/                      # Main application code
│   ├── api/                  # API endpoints
│   ├── core/                 # Core configuration and utilities
│   ├── models/               # Data models
│   ├── services/             # Service implementations
│   └── static/               # Static files
│       ├── chat.html         # Main chat interface
│       └── test/             # Test HTML files
├── data/                     # CSV data storage
├── docs/                     # Documentation
│   ├── architecture/         # System design and architecture docs
│   └── setup/                # Setup and installation guides
├── tests/                    # Test files organized by category
│   ├── run_all_tests.py      # Test runner script
│   ├── test_api.py           # API tests
│   ├── test_chatbot.py       # Chatbot tests
│   ├── test_comprehensive.py # Comprehensive tests
│   ├── test_conversation_scenarios.py # Conversation tests
│   ├── test_csv_storage.py   # Storage tests
│   └── test_performance.py   # Performance tests
├── .env                      # Environment variables
├── .env.example              # Example environment file
├── requirements.txt          # Python dependencies
└── README.md                 # This file
```

## Getting Started

### Prerequisites

- Python 3.9+
- OpenAI API key (for production use)

### Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/simple_llm_chatbot.git
   cd simple_llm_chatbot
   ```

2. Create and activate a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Copy the example environment file and update it with your settings:
   ```
   cp .env.example .env
   ```

5. Edit the `.env` file to add your OpenAI API key and other configuration options.

### Running the Application

1. Start the FastAPI backend:
   ```
   uvicorn app.main:app --reload
   ```

2. Access the API documentation at `http://localhost:8000/docs`

3. For the chat interface, open `chat.html` in your browser.

## Testing

The application includes a testing mode that uses mock implementations of external services:

1. Set `TESTING=True` in your `.env` file
2. Run all tests using the test runner:
   ```
   python -m tests.run_all_tests
   ```

3. Or run specific test categories:
   ```
   # API Tests
   python -m tests.test_api
   python -m tests.test_chatbot
   
   # Functional Tests
   python -m tests.test_comprehensive
   python -m tests.test_conversation_scenarios
   
   # Storage Tests
   python -m tests.test_csv_storage
   
   # Performance Tests
   python -m tests.test_performance
   ```

For more detailed information about testing, please refer to the [Testing Guide](docs/setup/testing_guide.md) and [Test Scripts Reference](docs/setup/test_scripts_reference.md).

## Data Storage

The application stores lead information in CSV files located in the `data` directory. You can view and manage this data using any spreadsheet application like Microsoft Excel or LibreOffice Calc.

## Documentation

For more detailed information, please refer to the documentation in the `docs` directory:

- [Installation Guide](docs/setup/installation_guide.md)
- [Testing Guide](docs/setup/testing_guide.md)
- [System Design](docs/architecture/system_design.md)
- [Conversation Flow](docs/architecture/conversation_flow.md)
- [Development Journey](docs/project/development_journey.md) - A detailed history of the project's development process

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- [LiteLLM](https://github.com/BerriAI/litellm) for the LLM integration
- [Langflow](https://github.com/langflow-ai/langflow) for the conversation flow editor
- [FastAPI](https://fastapi.tiangolo.com/) for the API framework

# Simple LLM Chatbot v1

A lightweight pre-sales assistant chatbot built with LiteLLM, Langflow, and FastAPI.

## Overview

This project implements a conversational chatbot that acts as a pre-sales assistant for a software development company. The chatbot helps gather client requirements, extract key information about their project needs, and store lead data in Google Sheets for follow-up.

### Key Features

- **Natural Conversation Flow**: Engages users in a natural conversation to gather requirements
- **Information Extraction**: Identifies project type, timeline, budget, and other key details
- **Lead Storage**: Automatically stores lead information in Google Sheets
- **Flexible Architecture**: Built with modular components for easy extension
- **Modern LLM Integration**: Uses GPT-4o-mini via LiteLLM for intelligent responses
- **Testing Mode**: Supports testing without external dependencies using mock services

## Technology Stack

- **Backend**: FastAPI
- **LLM Integration**: LiteLLM with GPT-4o-mini
- **Conversation Flow**: Langflow
- **Data Storage**: Google Sheets API

## Getting Started

### Prerequisites

- Python 3.11+
- OpenAI API key
- Google Cloud account (for Google Sheets API)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/simple_llm_chatbot_v1.git
   cd simple_llm_chatbot_v1
   ```

2. Set up a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your API keys and configuration
   ```

5. Run the application:
   ```bash
   uvicorn app.main:app --reload
   ```

For detailed installation instructions, see the [Installation Guide](docs/setup/installation_guide.md).

## Testing

The application includes a testing mode that uses mock implementations of external services:

1. Enable testing mode in your `.env` file:
   ```
   TESTING=True
   ```

2. Run the application:
   ```bash
   python -m app.main
   ```

3. Run the test script:
   ```bash
   python -m tests.test_api
   ```

For detailed testing instructions, see the [Testing Guide](docs/setup/testing_guide.md).

## Documentation

- [System Architecture](docs/architecture/system_design.md)
- [API Reference](docs/api/api_reference.md)
- [Installation Guide](docs/setup/installation_guide.md)
- [Testing Guide](docs/setup/testing_guide.md)

## Development Roadmap

See [project_info.txt](project_info.txt) for the current development status and roadmap.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- OpenAI for the GPT models
- LiteLLM for simplified LLM integration
- Langflow for the conversation flow editor

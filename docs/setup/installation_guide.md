# Installation Guide

## Prerequisites

Before installing the chatbot system, ensure you have the following:

1. Python 3.11+ installed
2. pip package manager
3. Git (for version control)
4. OpenAI API key

## Step 1: Clone the Repository

```bash
git clone https://github.com/yourusername/simple_llm_chatbot_v1.git
cd simple_llm_chatbot_v1
```

## Step 2: Set Up Virtual Environment

```bash
# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# On Windows
venv\Scripts\activate
# On macOS/Linux
source venv/bin/activate
```

## Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

## Step 4: Configure Environment Variables

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Edit the `.env` file with your credentials:
   ```
   # OpenAI Configuration
   OPENAI_API_KEY=your_key_here
   
   # LiteLLM Configuration
   LITELLM_MODEL=gpt-4o-mini
   
   # Data Storage Configuration
   CSV_DATA_DIRECTORY=data
   CSV_LEADS_FILE=leads.csv
   
   # FastAPI Configuration
   API_HOST=0.0.0.0
   API_PORT=8000
   ```

## Step 5: Data Storage Setup

The application uses a local CSV file for storing lead data. The file will be automatically created when the first lead is stored. By default, the file is located at `data/leads.csv`.

You can customize the location by changing the `CSV_DATA_DIRECTORY` and `CSV_LEADS_FILE` settings in your `.env` file.

## Step 6: Run the Application

```bash
# Start the FastAPI server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Once the server is running, you can:
- Access the chat interface at: `http://localhost:8000/chat`
- Access the API documentation at: `http://localhost:8000/docs`
- Check the server health at: `http://localhost:8000/health`

## Step 7: Set Up Langflow (Optional)

If you want to modify the conversation flow:

1. Install Langflow:
   ```
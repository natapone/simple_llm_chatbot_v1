# Installation Guide

## Prerequisites

Before installing the chatbot system, ensure you have the following:

1. Python 3.11+ installed
2. pip package manager
3. Git (for version control)
4. Google Cloud account (for Google Sheets API)
5. OpenAI API key

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
   
   # Google Sheets Configuration
   GOOGLE_SHEETS_CREDENTIALS_FILE=path_to_credentials.json
   GOOGLE_SHEETS_SPREADSHEET_ID=your_spreadsheet_id
   
   # FastAPI Configuration
   API_HOST=0.0.0.0
   API_PORT=8000
   ```

## Step 5: Set Up Google Sheets API

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project
3. Enable the Google Sheets API
4. Create credentials (Service Account)
5. Download the JSON credentials file
6. Place the credentials file in a secure location
7. Update the `GOOGLE_SHEETS_CREDENTIALS_FILE` in your `.env` file

## Step 6: Create Google Sheet for Lead Storage

1. Create a new Google Sheet
2. Set up the following columns:
   - Timestamp
   - Client Name
   - Contact Information
   - Project Type
   - Requirements Summary
   - Timeline
   - Budget Range
   - Follow-up Status
3. Share the sheet with the service account email (from your credentials)
4. Copy the spreadsheet ID from the URL and update `GOOGLE_SHEETS_SPREADSHEET_ID` in your `.env` file

## Step 7: Run the Application

```bash
# Start the FastAPI server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## Step 8: Set Up Langflow (Optional)

If you want to modify the conversation flow:

1. Install Langflow:
   ```bash
   pip install langflow
   ```

2. Start Langflow:
   ```bash
   langflow
   ```

3. Access the Langflow UI at `http://localhost:7860`
4. Import the conversation flow from `flows/conversation_flow.json`

## Troubleshooting

### Common Issues

1. **API Key Issues**:
   - Ensure your OpenAI API key is valid and has sufficient credits
   - Check that the key is correctly set in the `.env` file

2. **Google Sheets API Issues**:
   - Verify that the API is enabled in your Google Cloud project
   - Ensure the service account has edit access to the spreadsheet
   - Check that the credentials file path is correct

3. **Dependency Issues**:
   - If you encounter dependency conflicts, try creating a fresh virtual environment
   - Ensure you're using a compatible Python version (3.9+)

### Getting Help

If you encounter issues not covered in this guide, please:

1. Check the project's GitHub issues
2. Consult the documentation in the `/docs` directory
3. Reach out to the development team 
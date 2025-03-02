"""
Configuration management for the application.
Loads environment variables and provides configuration settings.
"""

import os
from pathlib import Path
from typing import List, Optional, Dict, Any

from dotenv import load_dotenv
from pydantic import BaseModel, Field

# Load environment variables from .env file
dotenv_path = Path(".env")
if dotenv_path.exists():
    load_dotenv(dotenv_path=dotenv_path)


class LiteLLMSettings(BaseModel):
    """Settings for LiteLLM integration."""
    model: str = Field(default="gpt-4o-mini")
    temperature: float = Field(default=0.7)
    max_tokens: int = Field(default=1000)


class GoogleSheetsSettings(BaseModel):
    """Settings for Google Sheets integration."""
    credentials_file: str
    spreadsheet_id: str


class APISettings(BaseModel):
    """Settings for the FastAPI server."""
    host: str = Field(default="0.0.0.0")
    port: int = Field(default=8000)
    debug: bool = Field(default=False)


class SecuritySettings(BaseModel):
    """Security settings for the application."""
    api_key: str
    cors_origins: List[str] = Field(default=["http://localhost:3000"])


class LoggingSettings(BaseModel):
    """Logging settings for the application."""
    level: str = Field(default="INFO")
    file: Optional[str] = Field(default=None)


class Settings(BaseModel):
    """Main settings class for the application."""
    openai_api_key: str
    litellm: LiteLLMSettings = Field(default_factory=LiteLLMSettings)
    google_sheets: GoogleSheetsSettings
    api: APISettings = Field(default_factory=APISettings)
    security: SecuritySettings
    logging: LoggingSettings = Field(default_factory=LoggingSettings)


def get_settings() -> Settings:
    """
    Load settings from environment variables.
    
    Returns:
        Settings: Application settings
    """
    # OpenAI settings
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        raise ValueError("OPENAI_API_KEY environment variable is required")
    
    # LiteLLM settings
    litellm_model = os.getenv("LITELLM_MODEL", "gpt-4o-mini")
    litellm_temperature = float(os.getenv("LITELLM_TEMPERATURE", "0.7"))
    litellm_max_tokens = int(os.getenv("LITELLM_MAX_TOKENS", "1000"))
    
    # Google Sheets settings
    google_sheets_credentials_file = os.getenv("GOOGLE_SHEETS_CREDENTIALS_FILE")
    if not google_sheets_credentials_file:
        raise ValueError("GOOGLE_SHEETS_CREDENTIALS_FILE environment variable is required")
    
    google_sheets_spreadsheet_id = os.getenv("GOOGLE_SHEETS_SPREADSHEET_ID")
    if not google_sheets_spreadsheet_id:
        raise ValueError("GOOGLE_SHEETS_SPREADSHEET_ID environment variable is required")
    
    # API settings
    api_host = os.getenv("API_HOST", "0.0.0.0")
    api_port = int(os.getenv("API_PORT", "8000"))
    api_debug = os.getenv("DEBUG", "False").lower() in ("true", "1", "t")
    
    # Security settings
    api_key = os.getenv("API_KEY")
    if not api_key:
        raise ValueError("API_KEY environment variable is required")
    
    cors_origins_str = os.getenv("CORS_ORIGINS", "http://localhost:3000")
    cors_origins = [origin.strip() for origin in cors_origins_str.split(",")]
    
    # Logging settings
    log_level = os.getenv("LOG_LEVEL", "INFO")
    log_file = os.getenv("LOG_FILE")
    
    return Settings(
        openai_api_key=openai_api_key,
        litellm=LiteLLMSettings(
            model=litellm_model,
            temperature=litellm_temperature,
            max_tokens=litellm_max_tokens
        ),
        google_sheets=GoogleSheetsSettings(
            credentials_file=google_sheets_credentials_file,
            spreadsheet_id=google_sheets_spreadsheet_id
        ),
        api=APISettings(
            host=api_host,
            port=api_port,
            debug=api_debug
        ),
        security=SecuritySettings(
            api_key=api_key,
            cors_origins=cors_origins
        ),
        logging=LoggingSettings(
            level=log_level,
            file=log_file
        )
    )


# Create a singleton instance of settings
settings = get_settings() 
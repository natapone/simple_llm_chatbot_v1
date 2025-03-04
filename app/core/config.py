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


class CSVSettings(BaseModel):
    """Settings for CSV storage."""
    data_directory: str = Field(default="data")
    leads_file: str = Field(default="leads.csv")


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
    csv: CSVSettings = Field(default_factory=CSVSettings)
    api: APISettings = Field(default_factory=APISettings)
    security: SecuritySettings
    logging: LoggingSettings = Field(default_factory=LoggingSettings)
    testing: bool = Field(default=False)


def get_settings() -> Settings:
    """Get the application settings from environment variables."""
    # Load environment variables from .env file
    load_dotenv()
    
    # Get OpenAI API key
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        raise ValueError("OPENAI_API_KEY environment variable is not set")
    
    # Get LiteLLM settings
    litellm_settings = LiteLLMSettings(
        model=os.getenv("LITELLM_MODEL", "gpt-4o-mini"),
        temperature=float(os.getenv("LITELLM_TEMPERATURE", "0.7")),
        max_tokens=int(os.getenv("LITELLM_MAX_TOKENS", "1000"))
    )
    
    # Get CSV settings
    csv_settings = CSVSettings(
        data_directory=os.getenv("CSV_DATA_DIRECTORY", "data"),
        leads_file=os.getenv("CSV_LEADS_FILE", "leads.csv")
    )
    
    # Get API settings
    api_settings = APISettings(
        host=os.getenv("API_HOST", "0.0.0.0"),
        port=int(os.getenv("API_PORT", "8000")),
        debug=os.getenv("DEBUG", "False").lower() == "true"
    )
    
    # Get security settings
    api_key = os.getenv("API_KEY")
    if not api_key:
        raise ValueError("API_KEY environment variable is not set")
    
    cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
    security_settings = SecuritySettings(
        api_key=api_key,
        cors_origins=cors_origins
    )
    
    # Get logging settings
    logging_settings = LoggingSettings(
        level=os.getenv("LOG_LEVEL", "INFO"),
        file=os.getenv("LOG_FILE")
    )
    
    # Get testing mode
    testing = os.getenv("TESTING", "False").lower() == "true"
    
    return Settings(
        openai_api_key=openai_api_key,
        litellm=litellm_settings,
        csv=csv_settings,
        api=api_settings,
        security=security_settings,
        logging=logging_settings,
        testing=testing
    )


# Create a singleton instance of settings
settings = get_settings() 
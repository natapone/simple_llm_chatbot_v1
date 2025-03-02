"""
API dependencies for authentication and authorization.
"""

from fastapi import Header, HTTPException, Depends
from fastapi.security import APIKeyHeader

from app.core.config import settings
from app.core.logger import get_logger

# Get logger
logger = get_logger("api.dependencies")

# API key header
api_key_header = APIKeyHeader(name="X-API-Key")


async def verify_api_key(x_api_key: str = Header(...)) -> bool:
    """
    Verify that the provided API key is valid.
    
    Args:
        x_api_key: API key from request header
        
    Returns:
        True if the API key is valid
        
    Raises:
        HTTPException: If the API key is invalid
    """
    if x_api_key != settings.security.api_key:
        logger.warning("Invalid API key provided")
        raise HTTPException(
            status_code=401,
            detail="Invalid API key",
            headers={"WWW-Authenticate": "ApiKey"},
        )
    
    return True 
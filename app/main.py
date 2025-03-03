"""
Main application module for the chatbot API.
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
import uvicorn
import os
from pathlib import Path

from app.core.config import settings
from app.core.logger import get_logger
from app.api.chat import router as chat_router

# Get logger
logger = get_logger("main")

# Create FastAPI app
app = FastAPI(
    title="Pre-Sales Assistant Chatbot API",
    description="API for a pre-sales assistant chatbot using LiteLLM and Langflow",
    version="0.1.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.security.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files directory
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Include routers
app.include_router(chat_router)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler for unhandled exceptions."""
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"error": {"message": "An unexpected error occurred", "detail": str(exc)}},
    )


@app.get("/")
async def root():
    """Root endpoint for health check."""
    return {"status": "ok", "message": "Pre-Sales Assistant Chatbot API is running"}


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.get("/chat", response_class=HTMLResponse)
async def chat_page():
    """Serve the chat interface."""
    logger.info("Serving chat interface")
    chat_html_path = Path("app/static/chat.html")
    
    if not chat_html_path.exists():
        logger.error(f"Chat HTML file not found at {chat_html_path}")
        return "<h1>Error: Chat interface file not found</h1>"
    
    with open(chat_html_path, "r") as f:
        content = f.read()
    
    return content


if __name__ == "__main__":
    """Run the application when executed directly."""
    logger.info(f"Starting server on {settings.api.host}:{settings.api.port}")
    uvicorn.run(
        "app.main:app",
        host=settings.api.host,
        port=settings.api.port,
        reload=settings.api.debug
    )
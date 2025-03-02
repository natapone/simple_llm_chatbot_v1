"""
API routes for chat functionality.
"""

from typing import Dict, Any, Optional
import os

from fastapi import APIRouter, Depends, HTTPException, Header, Query
from pydantic import UUID4

from app.core.logger import get_logger
from app.models.chat import ChatRequest, ChatResponse, SessionInfo, LeadList, Lead, Message, MessageRole
from app.services.conversation_service import conversation_service
from app.services.sheets_service import sheets_service
from app.api.dependencies import verify_api_key

# Create router
router = APIRouter(prefix="/api", tags=["chat"])

# Get logger
logger = get_logger("api.chat")


@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    x_api_key: str = Header(...),
    _: bool = Depends(verify_api_key)
) -> Dict[str, Any]:
    """
    Send a message to the chatbot and receive a response.
    
    Args:
        request: Chat request with message and session ID
        x_api_key: API key for authentication
        
    Returns:
        Chat response with assistant message and conversation state
    """
    try:
        logger.info(f"Received chat request for session: {request.session_id}")
        
        # Process the message
        response = await conversation_service.process_message(
            session_id=request.session_id,
            message=request.message,
            user_info=request.user_info.dict() if request.user_info else None
        )
        
        logger.debug(f"Generated response for session: {request.session_id}")
        return response
    
    except Exception as e:
        logger.error(f"Error processing chat request: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")


@router.get("/sessions/{session_id}", response_model=SessionInfo)
async def get_session(
    session_id: str,
    x_api_key: str = Header(...),
    _: bool = Depends(verify_api_key)
) -> Dict[str, Any]:
    """
    Get information about a specific chat session.
    
    Args:
        session_id: Unique identifier for the session
        x_api_key: API key for authentication
        
    Returns:
        Session information including conversation history
    """
    try:
        logger.info(f"Retrieving session info: {session_id}")
        
        # Get session information
        session_info = await conversation_service.get_session_info(session_id)
        
        if not session_info:
            logger.warning(f"Session not found: {session_id}")
            raise HTTPException(status_code=404, detail="Session not found")
        
        logger.debug(f"Retrieved session info: {session_id}")
        return session_info
    
    except HTTPException:
        raise
    
    except Exception as e:
        logger.error(f"Error retrieving session info: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error retrieving session info: {str(e)}")


@router.delete("/sessions/{session_id}")
async def delete_session(
    session_id: str,
    x_api_key: str = Header(...),
    _: bool = Depends(verify_api_key)
) -> Dict[str, Any]:
    """
    Delete a specific chat session.
    
    Args:
        session_id: Unique identifier for the session
        x_api_key: API key for authentication
        
    Returns:
        Success message
    """
    try:
        logger.info(f"Deleting session: {session_id}")
        
        # Delete the session
        success = await conversation_service.delete_session(session_id)
        
        if not success:
            logger.warning(f"Session not found for deletion: {session_id}")
            raise HTTPException(status_code=404, detail="Session not found")
        
        logger.info(f"Session deleted: {session_id}")
        return {"status": "success", "message": "Session deleted successfully"}
    
    except HTTPException:
        raise
    
    except Exception as e:
        logger.error(f"Error deleting session: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error deleting session: {str(e)}")


@router.get("/leads", response_model=LeadList)
async def get_leads(
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    x_api_key: str = Header(...),
    _: bool = Depends(verify_api_key)
) -> LeadList:
    """
    Get a list of leads collected by the chatbot.
    
    Args:
        limit: Maximum number of leads to return
        offset: Number of leads to skip
        x_api_key: API key for authentication
        
    Returns:
        List of leads with pagination information
    """
    try:
        logger.info(f"Retrieving leads (limit={limit}, offset={offset})")
        
        # Get leads from Google Sheets
        leads_data = await sheets_service.get_leads(limit=limit, offset=offset)
        
        # Create a LeadList object
        lead_list = LeadList(
            total=leads_data["total"],
            limit=leads_data["limit"],
            offset=leads_data["offset"],
            leads=leads_data["leads"]
        )
        
        logger.debug(f"Retrieved {len(lead_list.leads)} leads")
        return lead_list
    
    except Exception as e:
        logger.error(f"Error retrieving leads: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error retrieving leads: {str(e)}")


@router.get("/leads/{lead_id}", response_model=Lead)
async def get_lead(
    lead_id: str,
    x_api_key: str = Header(...),
    _: bool = Depends(verify_api_key)
) -> Lead:
    """
    Get information about a specific lead.
    
    Args:
        lead_id: Unique identifier for the lead
        x_api_key: API key for authentication
        
    Returns:
        Lead information
    """
    try:
        logger.info(f"Retrieving lead: {lead_id}")
        
        # Get lead from Google Sheets
        lead = await sheets_service.get_lead_by_id(lead_id)
        
        if not lead:
            logger.warning(f"Lead not found: {lead_id}")
            raise HTTPException(status_code=404, detail="Lead not found")
        
        logger.debug(f"Retrieved lead: {lead_id}")
        return lead
    
    except HTTPException:
        raise
    
    except Exception as e:
        logger.error(f"Error retrieving lead: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error retrieving lead: {str(e)}")


@router.put("/leads/{lead_id}/status")
async def update_lead_status(
    lead_id: str,
    status: str,
    x_api_key: str = Header(...),
    _: bool = Depends(verify_api_key)
) -> Dict[str, Any]:
    """
    Update the follow-up status of a lead.
    
    Args:
        lead_id: Unique identifier for the lead
        status: New status value
        x_api_key: API key for authentication
        
    Returns:
        Success message
    """
    try:
        logger.info(f"Updating lead status: {lead_id} -> {status}")
        
        # Update lead status in Google Sheets
        success = await sheets_service.update_lead_status(lead_id, status)
        
        if not success:
            logger.warning(f"Lead not found for status update: {lead_id}")
            raise HTTPException(status_code=404, detail="Lead not found")
        
        logger.info(f"Lead status updated: {lead_id} -> {status}")
        return {"status": "success", "message": "Lead status updated successfully"}
    
    except HTTPException:
        raise
    
    except Exception as e:
        logger.error(f"Error updating lead status: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error updating lead status: {str(e)}")


@router.post("/test/create-lead", response_model=Lead)
async def create_test_lead(
    x_api_key: str = Header(...),
    _: bool = Depends(verify_api_key)
) -> Lead:
    """
    Create a test lead for testing purposes.
    Only available in testing mode.
    
    Args:
        x_api_key: API key for authentication
        
    Returns:
        Created lead information
    """
    try:
        # Check if we're in testing mode
        if os.getenv("TESTING", "False").lower() not in ("true", "1", "t"):
            logger.warning("Attempted to create test lead in non-testing mode")
            raise HTTPException(status_code=403, detail="This endpoint is only available in testing mode")
        
        logger.info("Creating test lead")
        
        # Create a test lead
        import uuid
        from datetime import datetime
        
        lead_id = f"test-lead-{uuid.uuid4()}"
        
        # Create a lead
        lead = Lead(
            id=lead_id,
            client_name="Test User",
            contact_info="test@example.com",
            project_type="Website",
            requirements_summary="A simple website with contact form",
            timeline="2 months",
            budget_range="$5,000-$10,000",
            follow_up_status="pending",
            created_at=datetime.utcnow(),
            conversation_history=[
                Message(
                    role=MessageRole.USER,
                    content="I need a website for my business",
                    timestamp=datetime.utcnow()
                ),
                Message(
                    role=MessageRole.ASSISTANT,
                    content="I'd be happy to help with that. What kind of features do you need?",
                    timestamp=datetime.utcnow()
                )
            ]
        )
        
        # Store the lead
        await sheets_service.store_lead(lead, "Test lead created for testing purposes")
        
        logger.info(f"Test lead created: {lead_id}")
        return lead
    
    except HTTPException:
        raise
    
    except Exception as e:
        logger.error(f"Error creating test lead: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error creating test lead: {str(e)}") 
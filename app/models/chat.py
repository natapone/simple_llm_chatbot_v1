"""
Data models for chat functionality.
"""

from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any, Union

from pydantic import BaseModel, Field, EmailStr


class ConversationState(str, Enum):
    """Enum representing the state of a conversation."""
    GREETING = "greeting"
    REQUIREMENT_GATHERING = "requirement_gathering"
    USE_CASE = "use_case"
    TIMELINE = "timeline"
    BUDGET = "budget"
    SUMMARIZATION = "summarization"
    CONTACT_COLLECTION = "contact_collection"
    CONFIRMATION = "confirmation"
    HANDOFF = "handoff"


class MessageRole(str, Enum):
    """Enum representing the role of a message sender."""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class UserInfo(BaseModel):
    """User information model."""
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None


class Message(BaseModel):
    """Chat message model."""
    role: MessageRole
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class CollectedInfo(BaseModel):
    """Information collected during the conversation."""
    project_type: Optional[str] = None
    requirements: Optional[List[str]] = None
    use_case: Optional[str] = None
    timeline: Optional[str] = None
    budget_range: Optional[str] = None
    client_name: Optional[str] = None
    contact_info: Optional[str] = None
    additional_notes: Optional[str] = None


class ConversationData(BaseModel):
    """Data about the current state of the conversation."""
    current_state: ConversationState = Field(default=ConversationState.GREETING)
    collected_info: CollectedInfo = Field(default_factory=CollectedInfo)
    history: List[Message] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ChatRequest(BaseModel):
    """Request model for chat endpoint."""
    message: str
    session_id: str
    user_info: Optional[UserInfo] = None


class ChatResponse(BaseModel):
    """Response model for chat endpoint."""
    response: str
    session_id: str
    conversation_state: Dict[str, Any]


class SessionInfo(BaseModel):
    """Information about a chat session."""
    session_id: str
    created_at: datetime
    last_active: datetime
    conversation_history: List[Message]
    collected_info: CollectedInfo


class Lead(BaseModel):
    """Lead information model."""
    id: str
    client_name: Optional[str] = None
    contact_info: Optional[str] = None
    project_type: Optional[str] = None
    requirements_summary: Optional[str] = None
    timeline: Optional[str] = None
    budget_range: Optional[str] = None
    follow_up_status: str = "pending"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    conversation_history: Optional[List[Message]] = None


class LeadList(BaseModel):
    """List of leads with pagination information."""
    total: int
    limit: int
    offset: int
    leads: List[Lead] 
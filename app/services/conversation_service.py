"""
Conversation service for managing chat interactions.
"""

import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple

from app.core.logger import get_logger
from app.models.chat import (
    Message, 
    MessageRole, 
    ConversationState, 
    ConversationData,
    CollectedInfo,
    Lead
)
from app.services.llm_service import llm_service
from app.services.sheets_service import sheets_service

# Get logger
logger = get_logger("conversation_service")

# In-memory storage for active conversations
# In a production environment, this would be replaced with a database
active_conversations: Dict[str, ConversationData] = {}


class ConversationService:
    """Service for managing conversations with users."""
    
    async def process_message(
        self, 
        session_id: str, 
        message: str, 
        user_info: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Process a user message and generate a response.
        
        Args:
            session_id: Unique identifier for the conversation session
            message: User message text
            user_info: Optional user information
            
        Returns:
            Dictionary with response and conversation state
        """
        # Get or create conversation data
        conversation = self._get_or_create_conversation(session_id)
        
        # Add user message to history
        user_message = Message(
            role=MessageRole.USER,
            content=message
        )
        conversation.history.append(user_message)
        
        # Update user info if provided
        if user_info:
            if user_info.get("name"):
                conversation.collected_info.client_name = user_info.get("name")
            if user_info.get("email"):
                conversation.collected_info.contact_info = user_info.get("email")
            elif user_info.get("phone"):
                conversation.collected_info.contact_info = user_info.get("phone")
        
        # Process the message based on the current state
        response, next_state = await self._process_state(conversation, message)
        
        # Update the conversation state
        conversation.current_state = next_state
        
        # Add assistant response to history
        assistant_message = Message(
            role=MessageRole.ASSISTANT,
            content=response
        )
        conversation.history.append(assistant_message)
        
        # Save the updated conversation
        active_conversations[session_id] = conversation
        
        # Check if we need to store a lead (when reaching handoff state)
        if next_state == ConversationState.HANDOFF:
            await self._store_lead(session_id)
        
        # Return the response and current state
        return {
            "response": response,
            "session_id": session_id,
            "conversation_state": {
                "current_step": next_state.value,
                "collected_info": conversation.collected_info.dict(exclude_none=True)
            }
        }
    
    def _get_or_create_conversation(self, session_id: str) -> ConversationData:
        """
        Get an existing conversation or create a new one.
        
        Args:
            session_id: Unique identifier for the conversation session
            
        Returns:
            ConversationData object
        """
        if session_id in active_conversations:
            return active_conversations[session_id]
        
        # Create a new conversation
        conversation = ConversationData()
        active_conversations[session_id] = conversation
        
        logger.info(f"Created new conversation: {session_id}")
        return conversation
    
    async def _process_state(
        self, 
        conversation: ConversationData, 
        message: str
    ) -> Tuple[str, ConversationState]:
        """
        Process a message based on the current conversation state.
        
        Args:
            conversation: Current conversation data
            message: User message text
            
        Returns:
            Tuple of (response text, next state)
        """
        current_state = conversation.current_state
        logger.debug(f"Processing message in state: {current_state}")
        
        # Extract entities based on the current state
        await self._extract_entities(conversation, message, current_state)
        
        # Determine the next state and generate a response
        if current_state == ConversationState.GREETING:
            return await self._handle_greeting(conversation, message)
        
        elif current_state == ConversationState.REQUIREMENT_GATHERING:
            return await self._handle_requirement_gathering(conversation, message)
        
        elif current_state == ConversationState.USE_CASE_UNDERSTANDING:
            return await self._handle_use_case(conversation, message)
        
        elif current_state == ConversationState.TIMELINE_EXPECTATIONS:
            return await self._handle_timeline(conversation, message)
        
        elif current_state == ConversationState.BUDGET_INQUIRY:
            return await self._handle_budget(conversation, message)
        
        elif current_state == ConversationState.SUMMARIZATION:
            return await self._handle_summarization(conversation, message)
        
        elif current_state == ConversationState.CONTACT_COLLECTION:
            return await self._handle_contact_collection(conversation, message)
        
        elif current_state == ConversationState.HANDOFF:
            return await self._handle_handoff(conversation, message)
        
        # Default fallback
        system_prompt = "You are a helpful pre-sales assistant for a software development company."
        response = await llm_service.generate_response(
            conversation.history,
            system_prompt
        )
        return response, current_state
    
    async def _extract_entities(
        self, 
        conversation: ConversationData, 
        message: str, 
        state: ConversationState
    ):
        """
        Extract relevant entities based on the current state.
        
        Args:
            conversation: Current conversation data
            message: User message text
            state: Current conversation state
        """
        try:
            if state == ConversationState.GREETING:
                # Extract project type
                entities = await llm_service.extract_entities(
                    message, 
                    ["project_type"]
                )
                if entities.get("project_type"):
                    conversation.collected_info.project_type = entities["project_type"]
            
            elif state == ConversationState.REQUIREMENT_GATHERING:
                # Extract requirements
                entities = await llm_service.extract_entities(
                    message, 
                    ["requirements"]
                )
                if entities.get("requirements"):
                    # Handle both string and list formats
                    if isinstance(entities["requirements"], str):
                        reqs = [req.strip() for req in entities["requirements"].split(",")]
                        conversation.collected_info.requirements = reqs
                    elif isinstance(entities["requirements"], list):
                        conversation.collected_info.requirements = entities["requirements"]
            
            elif state == ConversationState.USE_CASE_UNDERSTANDING:
                # Extract use case
                entities = await llm_service.extract_entities(
                    message, 
                    ["use_case"]
                )
                if entities.get("use_case"):
                    conversation.collected_info.use_case = entities["use_case"]
            
            elif state == ConversationState.TIMELINE_EXPECTATIONS:
                # Extract timeline
                entities = await llm_service.extract_entities(
                    message, 
                    ["timeline"]
                )
                if entities.get("timeline"):
                    conversation.collected_info.timeline = entities["timeline"]
            
            elif state == ConversationState.BUDGET_INQUIRY:
                # Extract budget range
                entities = await llm_service.extract_entities(
                    message, 
                    ["budget_range"]
                )
                if entities.get("budget_range"):
                    conversation.collected_info.budget_range = entities["budget_range"]
            
            elif state == ConversationState.CONTACT_COLLECTION:
                # Extract contact information
                entities = await llm_service.extract_entities(
                    message, 
                    ["contact_info", "client_name"]
                )
                if entities.get("contact_info"):
                    conversation.collected_info.contact_info = entities["contact_info"]
                if entities.get("client_name"):
                    conversation.collected_info.client_name = entities["client_name"]
        
        except Exception as e:
            logger.error(f"Error extracting entities: {str(e)}")
    
    async def _handle_greeting(
        self, 
        conversation: ConversationData, 
        message: str
    ) -> Tuple[str, ConversationState]:
        """Handle the greeting state."""
        system_prompt = """
        You are a pre-sales assistant for a software development company.
        Your goal is to understand the client's needs and gather information about their project.
        Be friendly, professional, and helpful.
        
        If the user has already mentioned a project type or specific requirements, acknowledge them and ask for more details.
        Otherwise, ask an open-ended question about their software development needs.
        """
        
        response = await llm_service.generate_response(
            conversation.history,
            system_prompt
        )
        
        # Transition to requirement gathering if project type is mentioned
        next_state = ConversationState.REQUIREMENT_GATHERING if conversation.collected_info.project_type else ConversationState.GREETING
        
        return response, next_state
    
    async def _handle_requirement_gathering(
        self, 
        conversation: ConversationData, 
        message: str
    ) -> Tuple[str, ConversationState]:
        """Handle the requirement gathering state."""
        system_prompt = """
        You are a pre-sales assistant for a software development company.
        Your goal is to gather specific requirements for the client's project.
        
        Ask about key features or functionalities they need.
        If they've already provided some requirements, acknowledge them and ask for any additional features.
        When you have a good understanding of their requirements, ask about the use case.
        """
        
        response = await llm_service.generate_response(
            conversation.history,
            system_prompt
        )
        
        # Transition to use case understanding if requirements are collected
        next_state = ConversationState.USE_CASE_UNDERSTANDING if conversation.collected_info.requirements else ConversationState.REQUIREMENT_GATHERING
        
        return response, next_state
    
    async def _handle_use_case(
        self, 
        conversation: ConversationData, 
        message: str
    ) -> Tuple[str, ConversationState]:
        """Handle the use case understanding state."""
        system_prompt = """
        You are a pre-sales assistant for a software development company.
        Your goal is to understand the use case for the client's project.
        
        Ask if the solution is for internal use or customer-facing.
        Ask about the target users and their needs.
        When you have a good understanding of the use case, ask about their timeline expectations.
        """
        
        response = await llm_service.generate_response(
            conversation.history,
            system_prompt
        )
        
        # Transition to timeline expectations if use case is collected
        next_state = ConversationState.TIMELINE_EXPECTATIONS if conversation.collected_info.use_case else ConversationState.USE_CASE_UNDERSTANDING
        
        return response, next_state
    
    async def _handle_timeline(
        self, 
        conversation: ConversationData, 
        message: str
    ) -> Tuple[str, ConversationState]:
        """Handle the timeline expectations state."""
        system_prompt = """
        You are a pre-sales assistant for a software development company.
        Your goal is to understand the client's timeline expectations.
        
        Ask about their expected timeline for the project.
        Ask if they're looking for a prototype first or a full solution.
        When you have a good understanding of their timeline, transition to discussing budget.
        """
        
        response = await llm_service.generate_response(
            conversation.history,
            system_prompt
        )
        
        # Transition to budget inquiry if timeline is collected
        next_state = ConversationState.BUDGET_INQUIRY if conversation.collected_info.timeline else ConversationState.TIMELINE_EXPECTATIONS
        
        return response, next_state
    
    async def _handle_budget(
        self, 
        conversation: ConversationData, 
        message: str
    ) -> Tuple[str, ConversationState]:
        """Handle the budget inquiry state."""
        system_prompt = """
        You are a pre-sales assistant for a software development company.
        Your goal is to tactfully gather budget information.
        
        Ask indirectly about their budget range, such as:
        "Would you like recommendations based on different pricing options, or do you already have a budget range in mind?"
        
        Be respectful if they're hesitant to share budget information.
        After discussing budget, summarize what you've learned about their project.
        """
        
        response = await llm_service.generate_response(
            conversation.history,
            system_prompt
        )
        
        # Always transition to summarization after budget discussion
        next_state = ConversationState.SUMMARIZATION
        
        return response, next_state
    
    async def _handle_summarization(
        self, 
        conversation: ConversationData, 
        message: str
    ) -> Tuple[str, ConversationState]:
        """Handle the summarization state."""
        # Generate a summary of the collected information
        collected = conversation.collected_info
        summary_parts = []
        
        if collected.project_type:
            summary_parts.append(f"a {collected.project_type}")
        
        if collected.use_case:
            summary_parts.append(f"for {collected.use_case}")
        
        requirements_text = ""
        if collected.requirements:
            requirements_text = ", ".join(collected.requirements)
            summary_parts.append(f"with features like {requirements_text}")
        
        timeline_text = ""
        if collected.timeline:
            timeline_text = f"You prefer {collected.timeline}"
        
        budget_text = ""
        if collected.budget_range:
            budget_text = f"with a budget range of {collected.budget_range}"
        elif timeline_text:
            budget_text = "and are open to budget discussions"
        else:
            budget_text = "You are open to budget discussions"
        
        summary = f"To summarize, you need {' '.join(summary_parts)}. {timeline_text} {budget_text}. Is this correct?"
        
        # Check if the user confirms the summary
        if "yes" in message.lower() or "correct" in message.lower() or "right" in message.lower():
            response = "Great! Could you share your email or phone number so we can follow up with recommendations?"
            next_state = ConversationState.CONTACT_COLLECTION
        else:
            response = summary
            next_state = ConversationState.SUMMARIZATION
        
        return response, next_state
    
    async def _handle_contact_collection(
        self, 
        conversation: ConversationData, 
        message: str
    ) -> Tuple[str, ConversationState]:
        """Handle the contact collection state."""
        system_prompt = """
        You are a pre-sales assistant for a software development company.
        Your goal is to collect contact information from the client.
        
        If they've provided contact information, thank them and let them know you'll create a request for the pre-sales team.
        If they haven't provided contact information, politely ask for their email or phone number.
        Explain that this is for the pre-sales team to follow up with recommendations.
        """
        
        response = await llm_service.generate_response(
            conversation.history,
            system_prompt
        )
        
        # Transition to handoff if contact info is collected
        next_state = ConversationState.HANDOFF if conversation.collected_info.contact_info else ConversationState.CONTACT_COLLECTION
        
        return response, next_state
    
    async def _handle_handoff(
        self, 
        conversation: ConversationData, 
        message: str
    ) -> Tuple[str, ConversationState]:
        """Handle the handoff state."""
        system_prompt = """
        You are a pre-sales assistant for a software development company.
        Your goal is to conclude the conversation and set expectations for next steps.
        
        Thank the client for their time and information.
        Let them know that the pre-sales team will review their request and get in touch soon.
        Provide a friendly closing message.
        """
        
        response = await llm_service.generate_response(
            conversation.history,
            system_prompt
        )
        
        # Stay in handoff state
        next_state = ConversationState.HANDOFF
        
        return response, next_state
    
    async def _store_lead(self, session_id: str):
        """
        Store lead information in Google Sheets.
        
        Args:
            session_id: Unique identifier for the conversation session
        """
        try:
            # Get the conversation data
            conversation = active_conversations.get(session_id)
            if not conversation:
                logger.warning(f"Conversation not found for lead storage: {session_id}")
                return
            
            # Generate a summary of the conversation
            summary = await llm_service.summarize_conversation(conversation.history)
            
            # Create a lead object
            collected = conversation.collected_info
            lead = Lead(
                id=f"lead_{uuid.uuid4().hex[:8]}",
                client_name=collected.client_name,
                contact_info=collected.contact_info,
                project_type=collected.project_type,
                requirements_summary=", ".join(collected.requirements) if collected.requirements else None,
                timeline=collected.timeline,
                budget_range=collected.budget_range,
                follow_up_status="pending",
                created_at=datetime.utcnow()
            )
            
            # Store the lead in Google Sheets
            await sheets_service.store_lead(lead, summary)
            
            logger.info(f"Lead stored successfully: {lead.id}")
        
        except Exception as e:
            logger.error(f"Error storing lead: {str(e)}")
    
    async def get_session_info(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a specific chat session.
        
        Args:
            session_id: Unique identifier for the conversation session
            
        Returns:
            Dictionary with session information or None if not found
        """
        conversation = active_conversations.get(session_id)
        if not conversation:
            return None
        
        # Get the first and last message timestamps
        created_at = conversation.history[0].timestamp if conversation.history else datetime.utcnow()
        last_active = conversation.history[-1].timestamp if conversation.history else datetime.utcnow()
        
        return {
            "session_id": session_id,
            "created_at": created_at,
            "last_active": last_active,
            "conversation_history": conversation.history,
            "collected_info": conversation.collected_info
        }
    
    async def delete_session(self, session_id: str) -> bool:
        """
        Delete a specific chat session.
        
        Args:
            session_id: Unique identifier for the conversation session
            
        Returns:
            True if successful, False otherwise
        """
        if session_id in active_conversations:
            del active_conversations[session_id]
            logger.info(f"Session deleted: {session_id}")
            return True
        
        logger.warning(f"Session not found for deletion: {session_id}")
        return False


# Create a singleton instance
conversation_service = ConversationService() 
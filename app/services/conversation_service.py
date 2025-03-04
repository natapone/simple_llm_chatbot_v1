"""
Conversation service for managing chat interactions.
"""

import logging
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
from app.services.llm_service import llm_service, LLMService
from app.services.csv_service import CSVService

# Configure logging
logger = logging.getLogger(__name__)

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
        try:
            logger.info(f"Processing message for session {session_id}")
            
            # Get or create conversation data
            conversation = self._get_or_create_conversation(session_id)
            
            # Store session_id in metadata
            conversation.metadata["session_id"] = session_id
            
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
            
            # Store the updated conversation
            self._store_conversation(session_id, conversation)
            
            # Check if we need to store a lead (when reaching handoff state)
            if next_state == ConversationState.HANDOFF and conversation.metadata.get("confirmed", False):
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
            
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            return {
                "response": "I'm sorry, but I encountered an error processing your message. Please try again.",
                "session_id": session_id,
                "conversation_state": {"state": "error"}
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
        
        elif current_state == ConversationState.USE_CASE:
            return await self._handle_use_case(conversation, message)
        
        elif current_state == ConversationState.TIMELINE:
            return await self._handle_timeline(conversation, message)
        
        elif current_state == ConversationState.BUDGET:
            return await self._handle_budget(conversation, message)
        
        elif current_state == ConversationState.SUMMARIZATION:
            return await self._handle_summarization(conversation, message)
        
        elif current_state == ConversationState.CONTACT_COLLECTION:
            return await self._handle_contact_collection(conversation, message)
        
        elif current_state == ConversationState.CONFIRMATION:
            return await self._handle_confirmation(conversation, message)
        
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
                    if isinstance(entities["requirements"], list):
                        conversation.collected_info.requirements = entities["requirements"]
                    else:
                        conversation.collected_info.requirements = [entities["requirements"]]
            
            elif state == ConversationState.USE_CASE:
                # Extract use case
                entities = await llm_service.extract_entities(
                    message, 
                    ["use_case"]
                )
                if entities.get("use_case"):
                    conversation.collected_info.use_case = entities["use_case"]
            
            elif state == ConversationState.TIMELINE:
                # Extract timeline
                entities = await llm_service.extract_entities(
                    message, 
                    ["timeline"]
                )
                if entities.get("timeline"):
                    conversation.collected_info.timeline = entities["timeline"]
            
            elif state == ConversationState.BUDGET:
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
                    logger.info(f"Collected contact info: {entities['contact_info']}")
                
                if entities.get("client_name"):
                    conversation.collected_info.client_name = entities["client_name"]
                    logger.info(f"Collected client name: {entities['client_name']}")
            
            elif state == ConversationState.CONFIRMATION:
                # Extract confirmation
                entities = await llm_service.extract_entities(
                    message, 
                    ["confirmation"]
                )
                if entities.get("confirmation"):
                    confirmation = entities["confirmation"].lower()
                    conversation.metadata["confirmation"] = confirmation
                    logger.info(f"Collected confirmation: {confirmation}")
            
            elif state == ConversationState.HANDOFF:
                # Extract confirmation status
                entities = await llm_service.extract_entities(
                    message, 
                    ["confirmation", "corrections"]
                )
                if entities.get("confirmation"):
                    conversation.metadata["confirmation"] = entities["confirmation"]
                if entities.get("corrections"):
                    conversation.metadata["corrections"] = entities["corrections"]
                    # Update collected info based on corrections
                    if isinstance(entities["corrections"], dict):
                        for key, value in entities["corrections"].items():
                            if hasattr(conversation.collected_info, key):
                                setattr(conversation.collected_info, key, value)
        
        except Exception as e:
            logger.error(f"Error extracting entities: {str(e)}")
            # Continue with conversation even if entity extraction fails
    
    async def _handle_greeting(
        self, 
        conversation: ConversationData, 
        message: str
    ) -> Tuple[str, ConversationState]:
        """Handle the greeting state of the conversation."""
        logger.debug("Handling greeting state")
        
        system_prompt = """
        You are a pre-sales assistant for a software development company. 
        Keep your response concise and friendly (under 100 words).
        Ask about the client's software development needs in a simple, direct way.
        Don't provide a list of services - just ask what they need help with.
        Use plain text only - no markdown, no asterisks, no special formatting.
        """
        
        response = await llm_service.generate_response(
            conversation.history,
            system_prompt
        )
        
        return response, ConversationState.REQUIREMENT_GATHERING
    
    async def _handle_requirement_gathering(
        self, 
        conversation: ConversationData, 
        message: str
    ) -> Tuple[str, ConversationState]:
        """Handle the requirement gathering state of the conversation."""
        logger.debug("Handling requirement gathering state")
        
        system_prompt = """
        You are gathering requirements for a software project.
        Ask 1-2 specific questions about key features they need.
        Keep your response under 80 words.
        Be friendly but direct.
        Use plain text only - no markdown, no asterisks, no special formatting.
        """
        
        response = await llm_service.generate_response(
            conversation.history,
            system_prompt
        )
        
        return response, ConversationState.USE_CASE
    
    async def _handle_use_case(
        self, 
        conversation: ConversationData, 
        message: str
    ) -> Tuple[str, ConversationState]:
        """Handle the use case understanding state of the conversation."""
        logger.debug("Handling use case understanding state")
        
        system_prompt = """
        Ask about the intended use case for this software (internal/customer-facing).
        Keep your response under 70 words.
        Ask only 1 clear question about their use case.
        Use plain text only - no markdown, no asterisks, no special formatting.
        """
        
        response = await llm_service.generate_response(
            conversation.history,
            system_prompt
        )
        
        return response, ConversationState.TIMELINE
    
    async def _handle_timeline(
        self, 
        conversation: ConversationData, 
        message: str
    ) -> Tuple[str, ConversationState]:
        """Handle the timeline expectations state of the conversation."""
        logger.debug("Handling timeline expectations state")
        
        system_prompt = """
        Ask about their project timeline in a direct way.
        Keep your response under 60 words.
        Just ask when they need the project completed.
        Use plain text only - no markdown, no asterisks, no special formatting.
        """
        
        response = await llm_service.generate_response(
            conversation.history,
            system_prompt
        )
        
        return response, ConversationState.BUDGET
    
    async def _handle_budget(
        self, 
        conversation: ConversationData, 
        message: str
    ) -> Tuple[str, ConversationState]:
        """Handle the budget inquiry state of the conversation."""
        logger.debug("Handling budget inquiry state")
        
        system_prompt = """
        Ask about budget range tactfully.
        Keep your response under 70 words.
        Be direct but polite.
        Don't list specific price ranges - just ask what their budget is.
        Use plain text only - no markdown, no asterisks, no special formatting.
        """
        
        response = await llm_service.generate_response(
            conversation.history,
            system_prompt
        )
        
        # After budget inquiry, move to summarization
        return response, ConversationState.SUMMARIZATION
    
    async def _handle_summarization(
        self, 
        conversation: ConversationData, 
        message: str
    ) -> Tuple[str, ConversationState]:
        """Handle the summarization state of the conversation."""
        logger.debug("Handling summarization state")
        
        # Generate a summary of the conversation
        summary = await llm_service.summarize_conversation(conversation.history)
        
        # Store the summary in the conversation metadata
        conversation.metadata["summary"] = summary
        
        # Check if we have contact information
        if conversation.collected_info.contact_info:
            # If we already have contact info, go to confirmation
            system_prompt = """
            Provide a clear summary of what you've understood about their project needs.
            Format as a bulleted list with hyphens.
            Include all key details: project type, requirements, timeline, budget, etc.
            End by asking them to confirm if the information is correct.
            Explicitly ask them to type "confirm" if everything is correct.
            If something is wrong, ask them to tell you what needs to be corrected.
            Keep your response under 150 words.
            Use plain text only - no markdown, no asterisks, no special formatting.
            """
            
            response = await llm_service.generate_response(
                conversation.history,
                system_prompt
            )
            
            return response, ConversationState.CONFIRMATION
        else:
            # If we don't have contact info, go to contact collection
            system_prompt = """
            Provide a clear summary of what you've understood about their project needs.
            Format as a bulleted list with hyphens.
            Include all key details: project type, requirements, timeline, budget, etc.
            End by asking for their contact information (email or phone).
            Keep your response under 150 words.
            Use plain text only - no markdown, no asterisks, no special formatting.
            """
            
            response = await llm_service.generate_response(
                conversation.history,
                system_prompt
            )
            
            return response, ConversationState.CONTACT_COLLECTION
    
    async def _handle_contact_collection(
        self, 
        conversation: ConversationData, 
        message: str
    ) -> Tuple[str, ConversationState]:
        """Handle the contact collection state of the conversation."""
        logger.debug("Handling contact collection state")
        
        # Extract contact information from the message
        await self._extract_entities(conversation, message, ConversationState.CONTACT_COLLECTION)
        
        # Check if we have contact information
        if conversation.collected_info.contact_info:
            # Move to confirmation state
            system_prompt = """
            Thank the client for providing their contact information.
            Provide a clear summary of what you've understood about their project needs.
            Format as a bulleted list with hyphens.
            Include all key details: project type, requirements, timeline, budget, contact info, etc.
            End by asking them to confirm if the information is correct.
            Explicitly ask them to type "confirm" if everything is correct.
            If something is wrong, ask them to tell you what needs to be corrected.
            Keep your response under 150 words.
            Use plain text only - no markdown, no asterisks, no special formatting.
            """
            
            response = await llm_service.generate_response(
                conversation.history,
                system_prompt
            )
            
            return response, ConversationState.CONFIRMATION
        else:
            # Ask again for contact information
            system_prompt = """
            Politely ask again for their contact information (email or phone).
            Explain that this is needed to follow up on their project requirements.
            Keep your response under 50 words.
            Use plain text only - no markdown, no asterisks, no special formatting.
            """
            
            response = await llm_service.generate_response(
                conversation.history,
                system_prompt
            )
            
            return response, ConversationState.CONTACT_COLLECTION
    
    async def _handle_handoff(
        self, 
        conversation: ConversationData, 
        message: str
    ) -> Tuple[str, ConversationState]:
        """Handle the handoff state of the conversation."""
        logger.debug("Handling handoff state")
        
        # We've already saved the lead information in the confirmation handler
        # Just stay in the handoff state
        system_prompt = """
        Thank the client for their time.
        Let them know that a team member will contact them soon to discuss their project further.
        Keep your response under 60 words.
        Use plain text only - no markdown, no asterisks, no special formatting.
        """
        
        response = await llm_service.generate_response(
            conversation.history,
            system_prompt
        )
        
        return response, ConversationState.HANDOFF
    
    async def _handle_confirmation(
        self, 
        conversation: ConversationData, 
        message: str
    ) -> Tuple[str, ConversationState]:
        """Handle the confirmation state of the conversation."""
        logger.debug("Handling confirmation state")
        
        # Extract confirmation from the message
        await self._extract_entities(conversation, message, ConversationState.CONFIRMATION)
        
        # Get confirmation status from metadata
        confirmation = conversation.metadata.get("confirmation", "").lower()
        
        if confirmation in ["yes", "confirm", "correct", "right", "looks good", "good"]:
            # User confirmed the information
            logger.info("User confirmed information, proceeding to handoff")
            
            # Mark as confirmed in metadata
            conversation.metadata["confirmed"] = True
            
            # Note: Lead will be saved when transitioning to HANDOFF state
            
            system_prompt = """
            Thank the client for confirming their information.
            Let them know that a team member will contact them soon to discuss their project further.
            Keep your response under 60 words.
            Use plain text only - no markdown, no asterisks, no special formatting.
            """
            
            response = await llm_service.generate_response(
                conversation.history,
                system_prompt
            )
            
            return response, ConversationState.HANDOFF
        
        elif confirmation in ["no", "incorrect", "wrong", "not right", "needs correction"]:
            # User indicated information is incorrect
            logger.info("User indicated information is incorrect, asking for corrections")
            
            system_prompt = """
            Apologize for the misunderstanding.
            Ask the client specifically what information needs to be corrected.
            Mention that they can provide corrections for any of these categories:
            - Project type/requirements
            - Use case
            - Timeline
            - Budget
            - Contact information
            Keep your response under 80 words.
            Use plain text only - no markdown, no asterisks, no special formatting.
            """
            
            response = await llm_service.generate_response(
                conversation.history,
                system_prompt
            )
            
            # Stay in the confirmation state to handle corrections
            return response, ConversationState.CONFIRMATION
        
        else:
            # Unclear response, ask for explicit confirmation
            logger.info("Unclear confirmation response, asking for explicit confirmation")
            
            system_prompt = """
            Politely ask the client to explicitly confirm if the information is correct.
            Ask them to type "confirm" if everything is correct, or to tell you what needs to be corrected.
            Keep your response under 60 words.
            Use plain text only - no markdown, no asterisks, no special formatting.
            """
            
            response = await llm_service.generate_response(
                conversation.history,
                system_prompt
            )
            
            return response, ConversationState.CONFIRMATION
    
    async def _store_lead(self, session_id: str):
        """
        Store the lead information.
        
        Args:
            session_id: The ID of the session
        """
        try:
            # Get the conversation data
            conversation = self._get_or_create_conversation(session_id)
            
            # Save the lead to the CSV file
            await self._save_lead_to_csv(conversation)
            
        except Exception as e:
            logger.error(f"Error storing lead: {str(e)}")
            # Continue with the conversation even if storing the lead fails
    
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

    async def _save_lead_to_csv(self, conversation: ConversationData) -> None:
        """Save the lead information to the CSV file.
        
        Args:
            conversation: The conversation data
        """
        try:
            # Create a summary of the conversation
            messages = conversation.history
            llm_service = LLMService()
            summary = await llm_service.summarize_conversation(messages)
            
            # Process requirements to ensure it's a list of strings
            requirements = conversation.collected_info.requirements
            if requirements is None:
                requirements_str = ""
            elif isinstance(requirements, list):
                # Filter out any non-string items and convert them to strings
                requirements_str = ", ".join(str(req) for req in requirements if req is not None)
            elif isinstance(requirements, dict):
                # If it's a dictionary, convert to a string representation
                requirements_str = ", ".join(f"{k}: {v}" for k, v in requirements.items())
            else:
                # For any other type, convert to string
                requirements_str = str(requirements)
            
            # Create a lead object
            lead = Lead(
                id=str(uuid.uuid4()),
                client_name=conversation.collected_info.client_name,
                contact_info=conversation.collected_info.contact_info,
                project_type=conversation.collected_info.project_type,
                requirements_summary=requirements_str,
                timeline=conversation.collected_info.timeline,
                budget_range=conversation.collected_info.budget_range,
                follow_up_status="pending",
                created_at=datetime.utcnow()
            )
            
            # Store the lead in the CSV file
            csv_service = CSVService()
            await csv_service.store_lead(lead, summary)
            
            logger.info(f"Saved lead to CSV file: {lead.id}")
            
        except Exception as e:
            logger.error(f"Error saving lead to CSV file: {str(e)}")
            # Continue with the conversation even if saving the lead fails

    def _store_conversation(self, session_id: str, conversation: ConversationData):
        """
        Store the conversation data in memory.
        
        Args:
            session_id: The ID of the session
            conversation: The conversation data to store
        """
        active_conversations[session_id] = conversation
        logger.debug(f"Stored conversation for session: {session_id}")


# Create a singleton instance
conversation_service = ConversationService() 
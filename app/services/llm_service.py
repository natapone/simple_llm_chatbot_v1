"""
LiteLLM service for interacting with OpenAI's GPT models.
"""

import json
import os
from typing import List, Dict, Any, Optional

import litellm
from litellm import completion

from app.core.config import settings
from app.core.logger import get_logger
from app.models.chat import Message, MessageRole

# Configure litellm
litellm.api_key = settings.openai_api_key

# Get logger
logger = get_logger("llm_service")


class LLMService:
    """Service for interacting with LLMs via LiteLLM."""
    
    def __init__(self):
        """Initialize the LLM service with configuration from settings."""
        self.model = settings.litellm.model
        self.temperature = settings.litellm.temperature
        self.max_tokens = settings.litellm.max_tokens
        self.testing = os.getenv("TESTING", "False").lower() in ("true", "1", "t")
        logger.info(f"Initialized LLM service with model: {self.model}, testing mode: {self.testing}")
    
    async def generate_response(
        self, 
        messages: List[Message], 
        system_prompt: Optional[str] = None
    ) -> str:
        """
        Generate a response from the LLM based on the conversation history.
        
        Args:
            messages: List of previous messages in the conversation
            system_prompt: Optional system prompt to guide the model's behavior
            
        Returns:
            The generated response text
        """
        # If in testing mode, return a mock response
        if self.testing:
            logger.info("Using mock LLM response in testing mode")
            return "This is a mock response from the LLM service in testing mode."
            
        # Convert Message objects to the format expected by LiteLLM
        formatted_messages = []
        
        # Add system prompt if provided
        if system_prompt:
            formatted_messages.append({
                "role": "system",
                "content": system_prompt
            })
        else:
            # Default system prompt for concise responses
            formatted_messages.append({
                "role": "system",
                "content": """You are a pre-sales assistant chatbot. Keep your responses concise, clear, and to the point.
                - Use short paragraphs (2-3 sentences max)
                - Use simple text formatting only (no markdown, no asterisks for emphasis)
                - Separate list items with simple hyphens followed by a space
                - Use plain text only
                - Use line breaks for readability
                - Avoid unnecessary details
                - Keep responses under 150 words
                - Be friendly but direct
                - Never use asterisks or other markdown symbols for formatting"""
            })
        
        # Add conversation history
        for msg in messages:
            formatted_messages.append({
                "role": msg.role.value,
                "content": msg.content
            })
        
        try:
            logger.debug(f"Sending request to LLM with {len(formatted_messages)} messages")
            
            # Call LiteLLM to generate a response
            response = completion(
                model=self.model,
                messages=formatted_messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            
            # Extract the response text
            response_text = response.choices[0].message.content
            logger.debug(f"Received response from LLM: {response_text[:50]}...")
            
            return response_text
        
        except Exception as e:
            logger.error(f"Error generating LLM response: {str(e)}")
            raise
    
    async def extract_entities(
        self, 
        text: str, 
        entity_types: List[str]
    ) -> Dict[str, Any]:
        """
        Extract specific entities from text using the LLM.
        
        Args:
            text: The text to extract entities from
            entity_types: List of entity types to extract (e.g., "project_type", "timeline")
            
        Returns:
            Dictionary of extracted entities
        """
        # If in testing mode, return mock entities
        if self.testing:
            logger.info("Using mock entity extraction in testing mode")
            mock_entities = {}
            for entity_type in entity_types:
                if entity_type == "confirmation":
                    # Check for confirmation keywords in the text
                    confirmation_keywords = ["yes", "confirm", "correct", "right", "ok", "okay", "sure", "agreed", "confirmed"]
                    rejection_keywords = ["no", "incorrect", "wrong", "not right", "needs correction"]
                    
                    text_lower = text.lower()
                    for keyword in confirmation_keywords:
                        if keyword.lower() in text_lower:
                            mock_entities[entity_type] = "yes"
                            break
                    else:
                        for keyword in rejection_keywords:
                            if keyword.lower() in text_lower:
                                mock_entities[entity_type] = "no"
                                break
                        else:
                            mock_entities[entity_type] = ""
                else:
                    mock_entities[entity_type] = f"Mock {entity_type}"
            return mock_entities
            
        # Special handling for confirmation entity
        if "confirmation" in entity_types and len(entity_types) == 1:
            confirmation_prompt = f"""
            Determine if the user is confirming or rejecting the information.
            
            User message: "{text}"
            
            If the user is confirming (using words like yes, confirm, correct, right, ok, okay, sure, agreed, etc.),
            respond with just the word: yes
            
            If the user is rejecting or pointing out errors (using words like no, incorrect, wrong, not right, etc.),
            respond with just the word: no
            
            If you can't clearly determine if they're confirming or rejecting, respond with an empty string.
            
            Your response should be ONLY one of these three options: "yes", "no", or ""
            """
            
            try:
                logger.debug("Extracting confirmation status")
                
                # Call LiteLLM to extract confirmation status
                response = completion(
                    model=self.model,
                    messages=[{"role": "user", "content": confirmation_prompt}],
                    temperature=0.1,
                    max_tokens=10
                )
                
                # Extract the response text
                response_text = response.choices[0].message.content.strip().lower()
                
                # Process the response
                if response_text == "yes":
                    return {"confirmation": "yes"}
                elif response_text == "no":
                    return {"confirmation": "no"}
                else:
                    return {"confirmation": ""}
                
            except Exception as e:
                logger.error(f"Error extracting confirmation status: {str(e)}")
                return {"confirmation": ""}
        
        # Standard entity extraction for other entity types
        prompt = f"""
        Extract the following information from the text below:
        {', '.join(entity_types)}
        
        Format the output as a valid JSON object with these keys.
        If you cannot find a particular entity, set its value to null.
        
        Text: {text}
        """
        
        try:
            logger.debug(f"Extracting entities: {entity_types}")
            
            # Call LiteLLM to extract entities
            response = completion(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=self.max_tokens
            )
            
            # Extract the response text
            response_text = response.choices[0].message.content
            
            # Parse the JSON response
            try:
                # Find JSON in the response
                start_idx = response_text.find('{')
                end_idx = response_text.rfind('}') + 1
                
                if start_idx >= 0 and end_idx > start_idx:
                    json_str = response_text[start_idx:end_idx]
                    entities = json.loads(json_str)
                    logger.debug(f"Extracted entities: {entities}")
                    return entities
                else:
                    logger.warning(f"Could not find JSON in response: {response_text}")
                    return {}
            
            except json.JSONDecodeError:
                logger.warning(f"Failed to parse JSON from response: {response_text}")
                return {}
            
        except Exception as e:
            logger.error(f"Error extracting entities: {str(e)}")
            return {}
    
    async def summarize_conversation(
        self, 
        messages: List[Message]
    ) -> str:
        """
        Generate a summary of the conversation.
        
        Args:
            messages: List of messages in the conversation
            
        Returns:
            A summary of the conversation
        """
        # If in testing mode, return a mock summary
        if self.testing:
            logger.info("Using mock conversation summary in testing mode")
            return "This is a mock summary of the conversation in testing mode."
            
        # Combine messages into a single text
        conversation_text = "\n".join([
            f"{msg.role.value.capitalize()}: {msg.content}" 
            for msg in messages
        ])
        
        prompt = f"""
        Summarize the key points from this conversation between a pre-sales assistant and a potential client.
        Focus on:
        1. The client's project requirements
        2. Use case and context
        3. Timeline expectations
        4. Budget information (if available)
        
        Keep the summary concise (under 100 words) and well-structured.
        
        Conversation:
        {conversation_text}
        """
        
        try:
            logger.debug("Generating conversation summary")
            
            # Call LiteLLM to generate a summary
            response = completion(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=self.max_tokens
            )
            
            # Extract the response text
            summary = response.choices[0].message.content
            logger.debug(f"Generated summary: {summary[:50]}...")
            
            return summary
        
        except Exception as e:
            logger.error(f"Error summarizing conversation: {str(e)}")
            raise


# Create a singleton instance
llm_service = LLMService() 
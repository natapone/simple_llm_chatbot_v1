"""
LiteLLM service for interacting with OpenAI's GPT models.
"""

import json
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
        logger.info(f"Initialized LLM service with model: {self.model}")
    
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
        # Convert Message objects to the format expected by LiteLLM
        formatted_messages = []
        
        # Add system prompt if provided
        if system_prompt:
            formatted_messages.append({
                "role": "system",
                "content": system_prompt
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
                temperature=0.1,  # Lower temperature for more deterministic output
                max_tokens=self.max_tokens
            )
            
            # Extract the response text
            response_text = response.choices[0].message.content
            
            # Parse the JSON response
            try:
                # Find JSON in the response (in case the model adds explanatory text)
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
            raise
    
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
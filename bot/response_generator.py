"""
Response Generator for AI-powered chat responses
"""
import logging
import re
import random
from typing import Optional, List, Dict

from models.chat_message import ChatMessage
from models.context_window import ContextWindow
from services.ai_service import AIService
from config.emotes import get_emotes


class ResponseGenerator:
    """Generates AI-powered responses for chat messages"""

    def __init__(self, ai_service: AIService):
        """
        Initialize the response generator

        Args:
            ai_service: The AI service for generating responses
        """
        self.ai_service = ai_service
        self.logger = logging.getLogger(__name__)

        # Maximum token length for responses
        self.max_response_length = 300

        # Cooldown tracking
        self.last_response_times = {}

    async def generate_response(self, message: ChatMessage, context: ContextWindow) -> Optional[str]:
        """
        Generate an AI response to a chat message

        Args:
            message: The chat message to respond to
            context: The context window for this channel

        Returns:
            str: The generated response or None if generation failed
        """
        try:
            # Extract prompt from message and context
            prompt = self._create_prompt(message, context)

            # Generate response from AI
            self.logger.debug("Sending prompt to AI service")
            raw_response = await self.ai_service.generate_response(prompt, self.max_response_length)

            if not raw_response:
                self.logger.warning("AI service returned empty response")
                return None

            # Post-process the response
            processed_response = self._post_process_response(raw_response, message.channel)

            self.logger.info(f"Generated response: {processed_response}")
            return processed_response

        except Exception as e:
            self.logger.error(f"Error generating response: {e}", exc_info=True)
            return None

    def _create_prompt(self, message: ChatMessage, context: ContextWindow) -> str:
        """
        Create a prompt for the AI based on message and context

        Args:
            message: The chat message to respond to
            context: The context window

        Returns:
            str: The formatted prompt
        """
        # Get recent context messages
        recent_messages = context.get_recent_messages(10)  # Last 10 messages

        # Format the context
        context_text = "\n".join([
            f"{msg.username}: {msg.message}" for msg in recent_messages
        ])

        # Build system prompt
        system_prompt = (
            "You are a friendly, entertaining Twitch chatbot. "
            "Keep responses short (1-2 sentences max) and conversational. "
            "Use Twitch emotes occasionally. Be helpful and engaging but concise. "
            "Avoid long explanations - Twitch chat is fast-paced.\n\n"
        )

        # Combine everything into the full prompt
        full_prompt = (
            f"{system_prompt}\n"
            f"Recent chat history:\n{context_text}\n\n"
            f"Respond to {message.username} who said: {message.message}"
        )

        return full_prompt

    def _post_process_response(self, response: str, channel: str) -> str:
        """
        Post-process the generated response

        Args:
            response: The raw AI response
            channel: The Twitch channel name

        Returns:
            str: The processed response
        """
        # Remove any quotes that the AI might have added
        response = re.sub(r'^["\']|["\']$', '', response.strip())

        # Ensure the response isn't too long for Twitch
        if len(response) > 500:
            response = response[:497] + "..."

        # Maybe add some Twitch emotes if not already present
        emotes = get_emotes()  # Fetch emotes dynamically
        all_emotes = list(emotes.get("all", []))  # Get all available emotes

        if random.random() < 0.3 and not any(emote in response for emote in all_emotes) and all_emotes:
        # Add a random emote at the end
            emote = random.choice(all_emotes)
            response = f"{response} {emote}"
        return response
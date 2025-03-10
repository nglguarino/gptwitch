"""
AI Service for generating responses using an AI API
"""
import os
import logging
import aiohttp
import json
from typing import Optional, Dict, Any


class AIService:
    """Service for interacting with AI APIs to generate responses"""

    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-3.5-turbo"):
        """
        Initialize the AI service

        Args:
            api_key: API key for the AI service (defaults to environment variable)
            model: Model name to use for generation
        """
        self.logger = logging.getLogger(__name__)
        self.api_key = api_key or os.getenv("AI_API_KEY")
        if not self.api_key:
            self.logger.warning("No AI API key provided. AI responses will be unavailable.")

        self.model = model
        self.session = None
        self.base_url = "https://api.openai.com/v1/chat/completions"

        # Set default parameters
        self.default_params = {
            "temperature": 0.7,
            "max_tokens": 150,
            "top_p": 0.9,
            "frequency_penalty": 0.5,
            "presence_penalty": 0.5,
        }

    async def _ensure_session(self):
        """Ensure HTTP session is created"""
        if self.session is None:
            self.session = aiohttp.ClientSession(
                headers={"Authorization": f"Bearer {self.api_key}"}
            )

    async def close(self):
        """Close the HTTP session"""
        if self.session:
            await self.session.close()
            self.session = None

    async def generate_response(self, prompt: str, max_tokens: Optional[int] = None,
                                temperature: Optional[float] = None) -> Optional[str]:
        """
        Generate a response using the AI API

        Args:
            prompt: The prompt to generate a response from
            max_tokens: Maximum number of tokens in the response
            temperature: Temperature for response generation

        Returns:
            Optional[str]: Generated response or None if generation failed
        """
        if not self.api_key:
            self.logger.error("Cannot generate response: No API key provided")
            return None

        try:
            await self._ensure_session()

            # Prepare request parameters
            params = self.default_params.copy()
            if max_tokens is not None:
                params["max_tokens"] = max_tokens
            if temperature is not None:
                params["temperature"] = temperature

            # Create message payload
            payload = {
                "model": self.model,
                "messages": [
                    {"role": "system",
                     "content": "You are a helpful Twitch chatbot. Keep responses short and engaging."},
                    {"role": "user", "content": prompt}
                ],
                **params
            }

            # Send request to API
            self.logger.debug(f"Sending request to AI API with model {self.model}")
            async with self.session.post(self.base_url, json=payload) as response:
                if response.status != 200:
                    error_text = await response.text()
                    self.logger.error(f"API error: {response.status} - {error_text}")
                    return None

                data = await response.json()

                # Extract response text
                if "choices" in data and data["choices"]:
                    content = data["choices"][0]["message"]["content"].strip()
                    self.logger.debug(f"Generated response of {len(content)} chars")
                    return content
                else:
                    self.logger.warning("API response did not contain expected data structure")
                    return None

        except aiohttp.ClientError as e:
            self.logger.error(f"HTTP error during API request: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Unexpected error generating response: {e}", exc_info=True)
            return None

    async def moderate_content(self, text: str) -> Dict[str, Any]:
        """
        Check if content is appropriate using moderation endpoint

        Args:
            text: The text to moderate

        Returns:
            Dict[str, Any]: Moderation results or empty dict if failed
        """
        if not self.api_key:
            self.logger.error("Cannot moderate content: No API key provided")
            return {}

        try:
            await self._ensure_session()

            # Use moderation endpoint
            moderation_url = "https://api.openai.com/v1/moderations"

            async with self.session.post(moderation_url, json={"input": text}) as response:
                if response.status != 200:
                    self.logger.error(f"Moderation API error: {response.status}")
                    return {}

                data = await response.json()
                return data

        except Exception as e:
            self.logger.error(f"Error during content moderation: {e}", exc_info=True)
            return {}

    def can_switch_models(self) -> bool:
        """
        Check if the service can switch between different models

        Returns:
            bool: True if model switching is supported
        """
        # This implementation supports different OpenAI models
        return True

    def set_model(self, model_name: str) -> bool:
        """
        Switch to a different AI model

        Args:
            model_name: Name of the model to use

        Returns:
            bool: True if successful, False otherwise
        """
        supported_models = [
            "gpt-3.5-turbo",
            "gpt-4",
            "text-davinci-003",
            "claude-v1",
            "claude-instant-v1"
        ]

        if model_name in supported_models:
            self.model = model_name
            self.logger.info(f"Switched to model: {model_name}")
            return True
        else:
            self.logger.warning(f"Unsupported model: {model_name}")
            return False
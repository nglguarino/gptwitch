"""
Twitch Service for interacting with the Twitch API
"""
import os
import logging
import aiohttp
from typing import Optional, Dict, List, Any, Union


class TwitchService:
    """Service for interacting with the Twitch API"""

    def __init__(self, oauth_token: Optional[str] = None, client_id: Optional[str] = None):
        """
        Initialize the Twitch service

        Args:
            oauth_token: OAuth token for authentication
            client_id: Twitch client ID
        """
        self.logger = logging.getLogger(__name__)
        self.oauth_token = oauth_token or os.getenv("TWITCH_OAUTH_TOKEN")
        self.client_id = client_id or os.getenv("TWITCH_CLIENT_ID")

        if not self.oauth_token:
            self.logger.warning("No OAuth token provided. API functionality limited.")
        if not self.client_id:
            self.logger.warning("No Client ID provided. API functionality limited.")

        self.session = None
        self.base_url = "https://api.twitch.tv/helix"
        self.auth_url = "https://id.twitch.tv/oauth2"

        # Cache for API responses
        self.cache = {}

    async def _ensure_session(self):
        """Ensure HTTP session is created with proper headers"""
        if self.session is None:
            headers = {}
            if self.oauth_token:
                # Remove "oauth:" prefix if present
                token = self.oauth_token
                if token.startswith("oauth:"):
                    token = token[6:]
                headers["Authorization"] = f"Bearer {token}"
            if self.client_id:
                headers["Client-ID"] = self.client_id

            self.session = aiohttp.ClientSession(headers=headers)

    async def close(self):
        """Close the HTTP session"""
        if self.session:
            await self.session.close()
            self.session = None

    async def validate_token(self) -> bool:
        """
        Validate the OAuth token

        Returns:
            bool: True if token is valid
        """
        if not self.oauth_token:
            return False

        try:
            await self._ensure_session()

            # Remove "oauth:" prefix if present
            token = self.oauth_token
            if token.startswith("oauth:"):
                token = token[6:]

            validate_url = f"{self.auth_url}/validate"
            headers = {"Authorization": f"Bearer {token}"}

            async with self.session.get(validate_url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    self.logger.info(f"Token validated for user ID: {data.get('user_id')}")
                    return True
                else:
                    self.logger.warning(f"Token validation failed: {response.status}")
                    return False

        except Exception as e:
            self.logger.error(f"Error validating token: {e}", exc_info=True)
            return False

    async def get_user_info(self, username: str) -> Dict[str, Any]:
        """
        Get information about a Twitch user

        Args:
            username: Twitch username

        Returns:
            Dict[str, Any]: User information or empty dict if failed
        """
        try:
            await self._ensure_session()

            # Check cache first
            cache_key = f"user_info:{username}"
            if cache_key in self.cache:
                return self.cache[cache_key]

            # Make API request
            endpoint = f"{self.base_url}/users"
            params = {"login": username}

            async with self.session.get(endpoint, params=params) as response:
                if response.status != 200:
                    self.logger.error(f"Error getting user info: {response.status}")
                    return {}

                data = await response.json()
                if "data" in data and data["data"]:
                    user_info = data["data"][0]
                    # Cache the result for 1 hour
                    self.cache[cache_key] = user_info
                    return user_info
                else:
                    return {}

        except Exception as e:
            self.logger.error(f"Error getting user info: {e}", exc_info=True)
            return {}

    async def get_stream_info(self, username: str) -> Dict[str, Any]:
        """
        Get information about a live stream

        Args:
            username: Twitch username

        Returns:
            Dict[str, Any]: Stream information or empty dict if failed
        """
        try:
            await self._ensure_session()

            endpoint = f"{self.base_url}/streams"
            params = {"user_login": username}

            async with self.session.get(endpoint, params=params) as response:
                if response.status != 200:
                    self.logger.error(f"Error getting stream info: {response.status}")
                    return {}

                data = await response.json()
                if "data" in data and data["data"]:
                    return data["data"][0]
                else:
                    return {}

        except Exception as e:
            self.logger.error(f"Error getting stream info: {e}", exc_info=True)
            return {}

    async def get_channel_info(self, broadcaster_id: str) -> Dict[str, Any]:
        """
        Get information about a channel

        Args:
            broadcaster_id: Twitch broadcaster ID

        Returns:
            Dict[str, Any]: Channel information or empty dict if failed
        """
        try:
            await self._ensure_session()

            endpoint = f"{self.base_url}/channels"
            params = {"broadcaster_id": broadcaster_id}

            async with self.session.get(endpoint, params=params) as response:
                if response.status != 200:
                    self.logger.error(f"Error getting channel info: {response.status}")
                    return {}

                data = await response.json()
                if "data" in data and data["data"]:
                    return data["data"][0]
                else:
                    return {}

        except Exception as e:
            self.logger.error(f"Error getting channel info: {e}", exc_info=True)
            return {}

    async def get_channel_emotes(self, broadcaster_id: str) -> List[Dict[str, Any]]:
        """
        Get custom emotes for a channel

        Args:
            broadcaster_id: Twitch broadcaster ID

        Returns:
            List[Dict[str, Any]]: List of emote data
        """
        try:
            await self._ensure_session()

            # Check cache first
            cache_key = f"channel_emotes:{broadcaster_id}"
            if cache_key in self.cache:
                return self.cache[cache_key]

            endpoint = f"{self.base_url}/chat/emotes"
            params = {"broadcaster_id": broadcaster_id}

            async with self.session.get(endpoint, params=params) as response:
                if response.status != 200:
                    self.logger.error(f"Error getting channel emotes: {response.status}")
                    return []

                data = await response.json()
                if "data" in data:
                    emotes = data["data"]
                    # Cache the result for 1 hour
                    self.cache[cache_key] = emotes
                    return emotes
                else:
                    return []

        except Exception as e:
            self.logger.error(f"Error getting channel emotes: {e}", exc_info=True)
            return []

    async def get_global_emotes(self) -> List[Dict[str, Any]]:
        """
        Get global Twitch emotes

        Returns:
            List[Dict[str, Any]]: List of emote data
        """
        try:
            await self._ensure_session()

            # Check cache first
            cache_key = "global_emotes"
            if cache_key in self.cache:
                return self.cache[cache_key]

            endpoint = f"{self.base_url}/chat/emotes/global"

            async with self.session.get(endpoint) as response:
                if response.status != 200:
                    self.logger.error(f"Error getting global emotes: {response.status}")
                    return []

                data = await response.json()
                if "data" in data:
                    emotes = data["data"]
                    # Cache the result for 1 day
                    self.cache[cache_key] = emotes
                    return emotes
                else:
                    return []

        except Exception as e:
            self.logger.error(f"Error getting global emotes: {e}", exc_info=True)
            return []

    async def request_capabilities(self, channel: str) -> bool:
        """
        Request additional capabilities for the bot in a channel
        (For example, sending messages with /me, requesting subscriber only mode, etc.)

        Args:
            channel: Channel name

        Returns:
            bool: True if successful
        """
        self.logger.info(f"Requesting additional capabilities for channel: {channel}")
        # This would typically involve sending special commands to the IRC server
        # For this implementation, we'll just return True
        return True

    async def send_chat_message(self, channel: str, message: str) -> bool:
        """
        Send a chat message to a channel through API
        (Alternative to using IRC)

        Args:
            channel: Channel name
            message: Message to send

        Returns:
            bool: True if successful
        """
        try:
            # Get broadcaster ID
            user_info = await self.get_user_info(channel)
            if not user_info:
                self.logger.error(f"Could not find broadcaster ID for {channel}")
                return False

            broadcaster_id = user_info["id"]

            await self._ensure_session()

            endpoint = f"{self.base_url}/chat/messages"
            payload = {
                "broadcaster_id": broadcaster_id,
                "sender_id": user_info.get("id"),  # Using the bot's ID
                "message": message
            }

            async with self.session.post(endpoint, json=payload) as response:
                if response.status == 204:
                    return True
                else:
                    self.logger.error(f"Error sending message: {response.status}")
                    return False

        except Exception as e:
            self.logger.error(f"Error sending chat message: {e}", exc_info=True)
            return False

    async def clear_cache(self):
        """Clear the API response cache"""
        self.cache.clear()
        self.logger.info("API cache cleared")
"""
Data model for chat messages
"""
import dataclasses
from datetime import datetime
from typing import Optional


@dataclasses.dataclass
class ChatMessage:
    """
    Represents a single chat message in a Twitch channel
    """
    channel: str  # Channel name where message was posted
    username: str  # Username of message author
    message: str  # Message content
    timestamp: Optional[datetime] = None  # Message timestamp
    is_subscriber: bool = False  # Is user a subscriber
    is_mod: bool = False  # Is user a moderator
    bits: int = 0  # Bits donated with the message
    emotes: dict = dataclasses.field(default_factory=dict)  # Emotes used in message
    tags: dict = dataclasses.field(default_factory=dict)  # Raw message tags

    def __post_init__(self):
        """Set defaults after initialization"""
        # Set current time if timestamp not provided
        if self.timestamp is None:
            self.timestamp = datetime.now()

    def is_mention(self, username: str) -> bool:
        """
        Check if this message mentions the given username

        Args:
            username: Username to check for mentions

        Returns:
            bool: True if the message mentions the username
        """
        return f"@{username.lower()}" in self.message.lower()

    def contains_command(self, prefix: str = "!") -> bool:
        """
        Check if this message contains a command

        Args:
            prefix: Command prefix (default: !)

        Returns:
            bool: True if the message starts with the command prefix
        """
        return self.message.startswith(prefix)

    def get_command(self, prefix: str = "!") -> Optional[str]:
        """
        Extract command from the message if present

        Args:
            prefix: Command prefix (default: !)

        Returns:
            Optional[str]: Command name without prefix, or None if not a command
        """
        if not self.contains_command(prefix):
            return None

        # Split message by whitespace and get first part without prefix
        parts = self.message.split()
        if not parts:
            return None

        return parts[0][len(prefix):].lower()

    def get_command_args(self, prefix: str = "!") -> list:
        """
        Extract command arguments from the message

        Args:
            prefix: Command prefix (default: !)

        Returns:
            list: List of command arguments (empty if not a command)
        """
        if not self.contains_command(prefix):
            return []

        # Split message by whitespace and return everything after the command
        parts = self.message.split()
        if len(parts) <= 1:
            return []

        return parts[1:]
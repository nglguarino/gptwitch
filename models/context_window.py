"""
Context window for maintaining chat history
"""
import logging
from collections import deque
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any

from models.chat_message import ChatMessage
from models.stream_event import StreamEvent


class ContextWindow:
    """
    Maintains a sliding window of recent chat messages and stream events
    for providing context to the AI response generator
    """

    def __init__(self, max_size: int = 100, max_age: Optional[timedelta] = None):
        """
        Initialize the context window

        Args:
            max_size: Maximum number of messages to keep in the window
            max_age: Maximum age of messages to keep (None = no limit)
        """
        self.messages = deque(maxlen=max_size)
        self.events = deque(maxlen=max_size // 2)  # Events queue is half the size of messages
        self.max_size = max_size
        self.max_age = max_age
        self.logger = logging.getLogger(__name__)

        # Track metadata about the context
        self.metadata: Dict[str, Any] = {
            "created_at": datetime.now(),
            "message_count": 0,
            "event_count": 0,
            "active_users": set(),
        }

    def add_message(self, message: ChatMessage) -> None:
        """
        Add a message to the context window

        Args:
            message: The chat message to add
        """
        self.messages.append(message)
        self.metadata["message_count"] += 1
        self.metadata["active_users"].add(message.username)
        self.logger.debug(f"Added message from {message.username} to context window")

        # Clean up old messages if needed
        if self.max_age:
            self._cleanup_old_messages()

    def add_event(self, event: StreamEvent) -> None:
        """
        Add a stream event to the context window

        Args:
            event: The stream event to add
        """
        self.events.append(event)
        self.metadata["event_count"] += 1
        if event.username:
            self.metadata["active_users"].add(event.username)
        self.logger.debug(f"Added event {event.event_type.value} to context window")

        # Clean up old events if needed
        if self.max_age:
            self._cleanup_old_events()

    def get_recent_messages(self, count: Optional[int] = None) -> List[ChatMessage]:
        """
        Get the most recent messages from the context window

        Args:
            count: Maximum number of messages to return (None = all)

        Returns:
            List[ChatMessage]: Recent messages
        """
        if count is None or count >= len(self.messages):
            return list(self.messages)
        else:
            # Get the last 'count' messages
            return list(self.messages)[-count:]

    def get_recent_events(self, count: Optional[int] = None) -> List[StreamEvent]:
        """
        Get the most recent events from the context window

        Args:
            count: Maximum number of events to return (None = all)

        Returns:
            List[StreamEvent]: Recent events
        """
        if count is None or count >= len(self.events):
            return list(self.events)
        else:
            # Get the last 'count' events
            return list(self.events)[-count:]

    def get_messages_by_user(self, username: str) -> List[ChatMessage]:
        """
        Get all messages from a specific user

        Args:
            username: The username to filter by

        Returns:
            List[ChatMessage]: Messages from the user
        """
        return [msg for msg in self.messages if msg.username.lower() == username.lower()]

    def get_active_users(self) -> List[str]:
        """
        Get a list of active users in the context window

        Returns:
            List[str]: List of usernames
        """
        return list(self.metadata["active_users"])

    def clear(self) -> None:
        """Clear all messages and events from the context window"""
        self.messages.clear()
        self.events.clear()
        self.metadata = {
            "created_at": datetime.now(),
            "message_count": 0,
            "event_count": 0,
            "active_users": set(),
        }
        self.logger.info("Context window cleared")

    def _cleanup_old_messages(self) -> None:
        """Remove messages older than max_age"""
        if not self.max_age:
            return

        cutoff_time = datetime.now() - self.max_age
        while self.messages and self.messages[0].timestamp < cutoff_time:
            self.messages.popleft()

    def _cleanup_old_events(self) -> None:
        """Remove events older than max_age"""
        if not self.max_age:
            return

        cutoff_time = datetime.now() - self.max_age
        while self.events and self.events[0].timestamp < cutoff_time:
            self.events.popleft()

    def get_context_summary(self) -> Dict[str, Any]:
        """
        Get a summary of the current context window state

        Returns:
            Dict[str, Any]: Context summary
        """
        now = datetime.now()
        active_users = self.get_active_users()

        return {
            "window_age_seconds": (now - self.metadata["created_at"]).total_seconds(),
            "message_count": self.metadata["message_count"],
            "event_count": self.metadata["event_count"],
            "current_message_count": len(self.messages),
            "current_event_count": len(self.events),
            "active_user_count": len(active_users),
            "active_users": active_users[:10],  # Limit to first 10 users
        }

    def __len__(self) -> int:
        """Get the total number of messages and events in the context window"""
        return len(self.messages) + len(self.events)

    def __repr__(self) -> str:
        """String representation of the context window"""
        return f"ContextWindow(messages={len(self.messages)}, events={len(self.events)})"
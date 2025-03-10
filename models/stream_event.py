"""
Data model for stream events
"""
import dataclasses
from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any


class EventType(Enum):
    """Types of stream events that can be tracked"""
    SUBSCRIPTION = "subscription"
    RESUBSCRIPTION = "resubscription"
    SUBSCRIPTION_GIFT = "subscription_gift"
    BITS = "bits"
    RAID = "raid"
    FOLLOW = "follow"
    HOST = "host"
    STREAM_START = "stream_start"
    STREAM_END = "stream_end"
    CUSTOM = "custom"


@dataclasses.dataclass
class StreamEvent:
    """
    Represents a stream event in a Twitch channel
    """
    channel: str  # Channel name where the event occurred
    event_type: EventType  # Type of event
    username: Optional[str] = None  # Username associated with the event (if applicable)
    timestamp: Optional[datetime] = None  # Event timestamp
    data: Dict[str, Any] = dataclasses.field(default_factory=dict)  # Additional event data

    def __post_init__(self):
        """Set defaults after initialization"""
        # Set current time if timestamp not provided
        if self.timestamp is None:
            self.timestamp = datetime.now()

    @classmethod
    def subscription(cls, channel: str, username: str, tier: str = "1",
                     months: int = 1, message: Optional[str] = None) -> 'StreamEvent':
        """
        Create a subscription event

        Args:
            channel: Channel name
            username: Username of subscriber
            tier: Subscription tier (1, 2, 3, or Prime)
            months: Months subscribed
            message: Subscription message (if any)

        Returns:
            StreamEvent: A subscription event
        """
        return cls(
            channel=channel,
            event_type=EventType.SUBSCRIPTION,
            username=username,
            data={
                "tier": tier,
                "months": months,
                "message": message,
            }
        )

    @classmethod
    def resubscription(cls, channel: str, username: str, tier: str = "1",
                       months: int = 1, message: Optional[str] = None) -> 'StreamEvent':
        """
        Create a resubscription event

        Args:
            channel: Channel name
            username: Username of resubscriber
            tier: Subscription tier (1, 2, 3, or Prime)
            months: Total months subscribed
            message: Resubscription message (if any)

        Returns:
            StreamEvent: A resubscription event
        """
        return cls(
            channel=channel,
            event_type=EventType.RESUBSCRIPTION,
            username=username,
            data={
                "tier": tier,
                "months": months,
                "message": message,
            }
        )

    @classmethod
    def subscription_gift(cls, channel: str, username: str, recipient: str,
                          tier: str = "1", months: int = 1) -> 'StreamEvent':
        """
        Create a subscription gift event

        Args:
            channel: Channel name
            username: Username of gift giver
            recipient: Username of gift recipient
            tier: Subscription tier (1, 2, 3)
            months: Months gifted

        Returns:
            StreamEvent: A subscription gift event
        """
        return cls(
            channel=channel,
            event_type=EventType.SUBSCRIPTION_GIFT,
            username=username,
            data={
                "recipient": recipient,
                "tier": tier,
                "months": months,
            }
        )

    @classmethod
    def bits(cls, channel: str, username: str, amount: int,
             message: Optional[str] = None) -> 'StreamEvent':
        """
        Create a bits event

        Args:
            channel: Channel name
            username: Username of bits sender
            amount: Number of bits
            message: Message with bits (if any)

        Returns:
            StreamEvent: A bits event
        """
        return cls(
            channel=channel,
            event_type=EventType.BITS,
            username=username,
            data={
                "amount": amount,
                "message": message,
            }
        )

    @classmethod
    def raid(cls, channel: str, username: str, viewers: int) -> 'StreamEvent':
        """
        Create a raid event

        Args:
            channel: Channel name
            username: Username of raider
            viewers: Number of raiders

        Returns:
            StreamEvent: A raid event
        """
        return cls(
            channel=channel,
            event_type=EventType.RAID,
            username=username,
            data={
                "viewers": viewers,
            }
        )

    @classmethod
    def follow(cls, channel: str, username: str) -> 'StreamEvent':
        """
        Create a follow event

        Args:
            channel: Channel name
            username: Username of follower

        Returns:
            StreamEvent: A follow event
        """
        return cls(
            channel=channel,
            event_type=EventType.FOLLOW,
            username=username,
        )

    @classmethod
    def host(cls, channel: str, username: str, viewers: int) -> 'StreamEvent':
        """
        Create a host event

        Args:
            channel: Channel name
            username: Username of hoster
            viewers: Number of viewers

        Returns:
            StreamEvent: A host event
        """
        return cls(
            channel=channel,
            event_type=EventType.HOST,
            username=username,
            data={
                "viewers": viewers,
            }
        )

    @classmethod
    def stream_start(cls, channel: str, game: Optional[str] = None,
                     title: Optional[str] = None) -> 'StreamEvent':
        """
        Create a stream start event

        Args:
            channel: Channel name
            game: Game category
            title: Stream title

        Returns:
            StreamEvent: A stream start event
        """
        return cls(
            channel=channel,
            event_type=EventType.STREAM_START,
            data={
                "game": game,
                "title": title,
            }
        )

    @classmethod
    def stream_end(cls, channel: str, duration: Optional[int] = None) -> 'StreamEvent':
        """
        Create a stream end event

        Args:
            channel: Channel name
            duration: Stream duration in seconds

        Returns:
            StreamEvent: A stream end event
        """
        return cls(
            channel=channel,
            event_type=EventType.STREAM_END,
            data={
                "duration": duration,
            }
        )
"""
Core TwitchBot class that handles IRC connections and message processing
"""
import asyncio
import logging
import re
from typing import List, Dict, Optional

import twitchio
from twitchio.ext import commands

from bot.command_handler import CommandHandler
from bot.response_generator import ResponseGenerator
from models.chat_message import ChatMessage
from models.context_window import ContextWindow
from services.ai_service import AIService
from services.twitch_service import TwitchService
from utils.queue_manager import MessageQueue


class TwitchBot(commands.Bot):
    """Main bot class that handles Twitch connection and message processing"""

    def __init__(self, username: str, token: str, channels: List[str]):
        """
        Initialize the TwitchBot

        Args:
            username: Bot's Twitch username
            token: OAuth token for authentication
            channels: List of channels to join
        """
        # Initialize the parent class
        super().__init__(token=token, prefix='!', initial_channels=channels)

        self.logger = logging.getLogger(__name__)
        self.username = username
        self.channels_list = channels

        # Initialize services
        self.ai_service = AIService()
        self.twitch_service = TwitchService(token)

        # Initialize handlers
        self.command_handler = CommandHandler(self)
        self.response_generator = ResponseGenerator(self.ai_service)

        # Initialize context tracking per channel
        self.context_windows: Dict[str, ContextWindow] = {}
        for channel in channels:
            self.context_windows[channel] = ContextWindow(max_size=50)

        # Message queue for processing
        self.message_queue = MessageQueue()

        # Start message processing task
        self.processing_task = None

    async def connect(self):
        """Connect to Twitch and start processing messages"""
        self.logger.info(f"Connecting to Twitch as {self.username}")

        # Start message processing
        self.processing_task = asyncio.create_task(self.process_message_queue())

        # Connect to Twitch
        await super().connect()
        self.logger.info("Successfully connected to Twitch")

    async def disconnect(self):
        """Disconnect from Twitch and clean up resources"""
        self.logger.info("Disconnecting from Twitch")

        # Cancel processing task
        if self.processing_task:
            self.processing_task.cancel()
            try:
                await self.processing_task
            except asyncio.CancelledError:
                pass

        # Close connections
        await self.ai_service.close()
        await self.twitch_service.close()
        await super().close()

        self.logger.info("Successfully disconnected from Twitch")

    async def event_ready(self):
        """Called once the bot has connected to Twitch"""
        self.logger.info(f"Bot {self.username} is ready and joined channels: {', '.join(self.channels_list)}")

        # Update bot capabilities
        for channel in self.channels_list:
            await self.twitch_service.request_capabilities(channel)

    async def event_message(self, message):
        """
        Called when a message is received in chat

        Args:
            message: The incoming message
        """
        # Ignore messages from the bot itself
        if message.author and message.author.name.lower() == self.username.lower():
            return

        # Create chat message model
        chat_message = ChatMessage(
            channel=message.channel.name,
            username=message.author.name if message.author else "Anonymous",
            message=message.content,
            timestamp=message.timestamp,
            is_subscriber=message.author.is_subscriber if message.author else False,
            is_mod=message.author.is_mod if message.author else False
        )

        # Add to channel context
        if chat_message.channel in self.context_windows:
            self.context_windows[chat_message.channel].add_message(chat_message)

        # Check if it's a command
        if message.content.startswith('!'):
            await self.handle_command(message)

        # Add message to queue for processing
        await self.message_queue.put(chat_message)

        # Process command with command handler
        await super().event_message(message)

    async def handle_command(self, message):
        """
        Handle bot commands

        Args:
            message: The command message
        """
        # Extract command name
        command_match = re.match(r'!(\w+)', message.content)
        if not command_match:
            return

        command = command_match.group(1).lower()

        # Pass to command handler
        await self.command_handler.handle_command(command, message)

    async def process_message_queue(self):
        """Process messages in the queue"""
        self.logger.info("Started message queue processing")

        try:
            while True:
                # Get next message from queue
                message = await self.message_queue.get()

                try:
                    # Check if AI should respond to this message
                    if self.should_respond_to(message):
                        await self.generate_and_send_response(message)
                except Exception as e:
                    self.logger.error(f"Error processing message: {e}", exc_info=True)

                # Mark as done
                self.message_queue.task_done()

        except asyncio.CancelledError:
            self.logger.info("Message queue processing task cancelled")
            raise

    def should_respond_to(self, message: ChatMessage) -> bool:
        """
        Determine if the bot should respond to a message

        Args:
            message: The chat message

        Returns:
            bool: True if the bot should respond
        """
        # Respond if the bot is mentioned
        if f"@{self.username.lower()}" in message.message.lower():
            return True

        # Add your custom conditions here
        # For example, respond randomly with a 5% chance to regular chat messages
        # if random.random() < 0.05:
        #     return True

        return False

    async def generate_and_send_response(self, message: ChatMessage):
        """
        Generate AI response and send it to chat

        Args:
            message: The triggering chat message
        """
        # Get channel context
        context = self.context_windows.get(message.channel)
        if not context:
            return

        # Generate response
        response = await self.response_generator.generate_response(message, context)

        if response:
            # Get channel object
            channel = self.get_channel(message.channel)
            if channel:
                # Send response to chat
                await channel.send(response)

                # Add bot response to context
                bot_message = ChatMessage(
                    channel=message.channel,
                    username=self.username,
                    message=response,
                    timestamp=None,  # Will be set to current time
                    is_subscriber=False,
                    is_mod=True
                )
                context.add_message(bot_message)
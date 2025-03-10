"""
Command handler for processing Twitch chat commands
"""
import logging
import inspect
from typing import Dict, Callable, Any, Optional
import twitchio


class CommandHandler:
    """Handles processing of chat commands"""

    def __init__(self, bot):
        """
        Initialize the command handler

        Args:
            bot: The TwitchBot instance
        """
        self.bot = bot
        self.logger = logging.getLogger(__name__)
        self.commands: Dict[str, Callable] = {}

        # Register commands
        self._register_commands()

    def _register_commands(self):
        """Register all command methods"""
        for name, method in inspect.getmembers(self, predicate=inspect.ismethod):
            if name.startswith("cmd_"):
                command_name = name[4:]  # Remove 'cmd_' prefix
                self.commands[command_name] = method
                self.logger.debug(f"Registered command: !{command_name}")

    async def handle_command(self, command: str, message):
        """
        Process a command

        Args:
            command: Command name without the prefix
            message: The message object
        """
        self.logger.debug(f"Handling command: !{command}")

        # Check if command exists
        if command in self.commands:
            try:
                await self.commands[command](message)
            except Exception as e:
                self.logger.error(f"Error executing command !{command}: {e}", exc_info=True)
        else:
            self.logger.debug(f"Unknown command: !{command}")

    async def cmd_help(self, message):
        """
        Help command that lists available commands

        Args:
            message: The message object
        """
        channel = message.channel
        commands_list = ", ".join([f"!{cmd}" for cmd in self.commands.keys()])
        await channel.send(f"Available commands: {commands_list}")

    async def cmd_info(self, message):
        """
        Information about the bot

        Args:
            message: The message object
        """
        channel = message.channel
        await channel.send("I'm an AI-powered Twitch chatbot! @ me in chat to talk with me.")

    async def cmd_ping(self, message):
        """
        Simple ping command

        Args:
            message: The message object
        """
        channel = message.channel
        await channel.send("Pong! 🏓")

    async def cmd_reset(self, message):
        """
        Reset the bot's context memory for this channel
        Only channel moderators can use this command

        Args:
            message: The message object
        """
        # Check if user is mod
        if not (message.author.is_mod or message.author.name.lower() == channel.name.lower()):
            await message.channel.send("❌ Only moderators can reset the bot's memory!")
            return

        # Reset context
        channel_name = message.channel.name
        if channel_name in self.bot.context_windows:
            self.bot.context_windows[channel_name].clear()
            await message.channel.send("🧠 My memory for this channel has been reset!")
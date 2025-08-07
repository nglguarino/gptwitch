#!/usr/bin/env python3
"""
Entry point for the Twitch AI Chatbot
"""
import asyncio
import logging
from bot.twitch_bot import TwitchBot
from config.settings import get_settings
from utils.logger import get_logger


# noinspection PyPep8Naming
async def main():
    """Main entry point for the bot"""
    # Setup logging
    get_logger()
    logger = logging.getLogger(__name__)
    logger.info("Starting Twitch AI Chatbot...")

    settings = get_settings()
    BOT_USERNAME = settings["BOT_USERNAME"]
    OAUTH_TOKEN = settings["TWITCH_OAUTH_TOKEN"]
    CHANNELS = settings["BOT_CHANNELS"]

    # Initialize bot
    bot = TwitchBot(BOT_USERNAME, OAUTH_TOKEN, CHANNELS)

    try:
        # Connect and start processing messages
        await bot.connect()

        # Keep the bot running
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        logger.info("Bot shutdown initiated via keyboard interrupt")
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
    finally:
        # Graceful shutdown
        await bot.disconnect()
        logger.info("Bot has been shut down")


if __name__ == "__main__":
    # Run the main function
    asyncio.run(main())
import logging
import os
import sys
from logging.handlers import RotatingFileHandler
from datetime import datetime


class TwitchBotLogger:
    """
    Logger utility for the Twitch AI Bot.
    Handles logging to both console and file with different log levels.
    """

    def __init__(self, log_level=logging.INFO, log_to_file=True, log_dir="logs"):
        self.logger = logging.getLogger("TwitchAIBot")
        self.logger.setLevel(log_level)
        self.logger.handlers = []  # Clear any existing handlers

        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)

        # File handler (optional)
        if log_to_file:
            # Create log directory if it doesn't exist
            if not os.path.exists(log_dir):
                os.makedirs(log_dir)

            # Create log file with timestamp
            log_file = os.path.join(
                log_dir,
                f"twitch_bot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
            )

            # Setup rotating file handler (10MB max size, keep 5 backup files)
            file_handler = RotatingFileHandler(
                log_file,
                maxBytes=10 * 1024 * 1024,  # 10MB
                backupCount=5
            )
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)

    def debug(self, message):
        """Log debug message"""
        self.logger.debug(message)

    def info(self, message):
        """Log info message"""
        self.logger.info(message)

    def warning(self, message):
        """Log warning message"""
        self.logger.warning(message)

    def error(self, message):
        """Log error message"""
        self.logger.error(message)

    def critical(self, message):
        """Log critical message"""
        self.logger.critical(message)

    def exception(self, message):
        """Log exception with traceback"""
        self.logger.exception(message)


# Default logger instance
default_logger = TwitchBotLogger()


def get_logger():
    """Get the default logger instance"""
    return default_logger
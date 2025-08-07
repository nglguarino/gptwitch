# GPTwitch Bot

A Twitch chatbot powered by AI that interacts with viewers and enhances stream engagement (in progress).

## Overview

GPTwitch is an intelligent chatbot designed for Twitch streamers that leverages AI to provide dynamic, context-aware responses to chat messages. The bot can engage with viewers, answer questions, generate content, and execute commands to enhance the streaming experience.

## Features

- **AI-Powered Responses**: Contextually relevant chat responses using modern AI models
- **Command Handler**: Custom commands for both viewers and moderators
- **Stream Event Detection**: Reacts to follows, subscriptions, and other Twitch events
- **Context Window**: Maintains conversation history for more coherent interactions
- **Emote Support**: Recognizes and uses channel emotes in responses
- **Queue Management**: Handles high-volume chat efficiently

## Project Structure

```
gptwitch/
├── .env                  # Environment variables (API keys, etc.)
├── .gitignore            # Git ignore file
├── requirements.txt      # Python dependencies
├── .venv/                # Python virtual environment
├── bot/                  # Core bot functionality
│   ├── command_handler.py
│   ├── main.py           # Entry point
│   ├── response_generator.py
│   └── twitch_bot.py
├── config/               # Configuration
│   ├── emotes.py
│   └── settings.py
├── models/               # Data models
│   ├── chat_message.py
│   ├── context_window.py
│   └── stream_event.py
├── services/             # External service integrations
│   ├── ai_service.py
│   └── twitch_service.py
└── utils/                # Helper utilities
    ├── logger.py
    └── queue_manager.py
```

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/gptwitch.git
   cd gptwitch
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   # On Windows
   .venv\Scripts\activate
   # On macOS/Linux
   source .venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file in the root directory with your credentials:
   ```
   # Twitch API Credentials
   TWITCH_CLIENT_ID=your_client_id_here
   TWITCH_CLIENT_SECRET=your_client_secret_here
   TWITCH_ACCESS_TOKEN=your_access_token_here
   TWITCH_REFRESH_TOKEN=your_refresh_token_here
   TWITCH_BOT_USERNAME=your_bot_username
   TWITCH_CHANNEL_NAME=channel_to_join

   # AI Service Credentials
   AI_API_KEY=your_ai_service_api_key
   AI_MODEL=gpt-4  # or other model name

   # Bot Configuration
   BOT_PREFIX=!
   CONTEXT_WINDOW_SIZE=10
   LOG_LEVEL=info
   ```

## Usage

1. Start the bot:
   ```bash
   python bot/main.py
   ```

2. Available commands (customize in `command_handler.py`):
   - `!help` - Display available commands
   - `!botinfo` - Information about the bot
   - `!respond [message]` - Force the bot to respond to a specific message

## Customization

### Adding Custom Commands

Edit `bot/command_handler.py` to add new commands:

```python
@register_command("mycommand")
def my_custom_command(message, args):
    return "This is my custom command response!"
```

### Changing AI Response Style

Modify the prompt templates in `services/ai_service.py` to adjust the bot's personality and response style.

## License

MIT License - See LICENSE file for details.

## Acknowledgements

- [Twitch API](https://dev.twitch.tv/docs/api/)
- [OpenAI API](https://platform.openai.com/docs/api-reference)

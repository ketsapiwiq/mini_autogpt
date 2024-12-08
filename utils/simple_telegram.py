import asyncio
import json
import os
from dotenv import load_dotenv
import random
import traceback
from telegram import Bot, Update
from telegram.error import TimedOut
from telegram.ext import CallbackContext
from utils.log import log
import time
import functools
import traceback

# Load environment variables from .env file
load_dotenv()

def run_async(coro):
    """
    Run an async coroutine in a way that works with different event loop scenarios.
    """
    try:
        return asyncio.run(coro)
    except RuntimeError:
        # If event loop is already running, create a task
        loop = asyncio.get_event_loop()
        return loop.create_task(coro)

def get_telegram_config():
    """
    Safely retrieve Telegram configuration from environment variables.
    
    Returns:
        tuple: (api_key, chat_id) or (None, None) if not configured
    """
    try:
        # Reload environment variables to ensure latest values
        load_dotenv(override=True)
        
        # Get API key and chat ID from environment variables
        api_key = os.getenv('TELEGRAM_API_KEY')
        chat_id = os.getenv('TELEGRAM_CHAT_ID')
        
        if not api_key or not chat_id:
            log("Telegram configuration incomplete. API key or Chat ID missing.")
            return None, None
        
        return api_key, chat_id
    except Exception as e:
        log(f"Error retrieving Telegram configuration: {e}")
        return None, None

class TelegramUtils:
    _instance = None
    
    @classmethod
    def get_instance(cls, api_key: str = None, chat_id: str = None):
        # If no credentials provided, try to get from environment
        if not api_key or not chat_id:
            api_key, chat_id = get_telegram_config()
        
        # If still no credentials, return None or raise an exception
        if not api_key or not chat_id:
            log("Cannot initialize Telegram: Missing credentials")
            return None

        if cls._instance is None:
            cls._instance = cls(api_key, chat_id)
        return cls._instance

    def __init__(self, api_key: str, chat_id: str):
        if not api_key:
            log("No API key provided for Telegram.")
            return

        self.api_key = api_key
        self.chat_id = str(chat_id)  # Ensure chat_id is a string
        self.bot = None
        self.conversation_history = []
        self._initialize_bot()

    def _initialize_bot(self):
        """Initialize the Telegram bot with proper error handling."""
        try:
            import telegram
            self.bot = telegram.Bot(token=self.api_key)
        except Exception as e:
            log(f"Error initializing Telegram bot: {e}")
            self.bot = None

    def send_message(self, message):
        """Interface method for sending a message."""
        try:
            # Add to conversation history
            self.add_to_conversation_history("Sent: " + message)
            
            # Send message with ellipsis
            run_async(self._send_message_async(message + "..."))
            return "Sent message successfully."
        except Exception as e:
            log(f"Error sending message: {e}")
            return f"Failed to send message: {e}"

    def ask_user(self, prompt):
        """Interface Method for Auto-GPT. Ask the user a question, return the answer"""
        max_attempts = 3
        for attempt in range(max_attempts):
            try:
                answer = run_async(self.ask_user_async(prompt=prompt))
                return answer
            except Exception as e:
                log(f"Telegram ask_user attempt {attempt + 1} failed: {e}")
                if attempt == max_attempts - 1:
                    return "User has not answered."
                time.sleep(2)

    async def ask_user_async(self, prompt, speak=False):
        """Async method to ask user a question and wait for response"""
        log("Asking user: " + prompt)
        await self._send_message_async(message=prompt, speak=speak)
        self.add_to_conversation_history("AI: " + prompt)
        
        log("Waiting for response on Telegram chat...")
        response = await self._wait_for_user_response()
        
        log(f"Response received from Telegram: {response}")
        return response

    async def _wait_for_user_response(self, timeout=300):
        """Wait for a user response with a timeout"""
        bot = Bot(token=self.api_key)
        last_update_id = None

        try:
            # Get initial updates to set the baseline
            initial_updates = await bot.get_updates(timeout=10)
            if initial_updates:
                last_update_id = initial_updates[-1].update_id

            start_time = time.time()
            while time.time() - start_time < timeout:
                try:
                    updates = await bot.get_updates(
                        offset=last_update_id + 1 if last_update_id else None, 
                        timeout=30
                    )

                    for update in updates:
                        if (update.message and 
                            update.message.text and 
                            str(update.message.chat.id) == self.chat_id):
                            
                            response = update.message.text
                            self.add_to_conversation_history("User: " + response)
                            return response

                        # Update last_update_id
                        if update.update_id:
                            last_update_id = update.update_id

                except Exception as e:
                    log(f"Error in update polling: {e}")
                    await asyncio.sleep(2)

            log("Timeout waiting for user response")
            return "No response received."

        except Exception as e:
            log(f"Critical error in waiting for response: {e}")
            return "Error in communication."

    async def _send_message_async(self, message, speak=False):
        """Send a message to Telegram, handling long messages"""
        if not self.bot:
            log("Telegram bot not initialized")
            return

        log(f"Sending message on Telegram: {message}")

        # Chunk messages longer than 2000 characters
        message_chunks = [message[i:i+2000] for i in range(0, len(message), 2000)]
        for chunk in message_chunks:
            await self.bot.send_message(chat_id=self.chat_id, text=chunk)

    def add_to_conversation_history(self, message):
        """Add a message to conversation history, keeping it limited"""
        self.conversation_history.append(message)
        # Keep only the last 20 messages
        self.conversation_history = self.conversation_history[-20:]

    def get_conversation_history(self):
        """Retrieve conversation history"""
        return self.conversation_history

    def get_last_few_messages(self, limit=5):
        """
        Fetch the last few messages from Telegram API and process them.
        
        Args:
            limit (int, optional): Number of messages to retrieve. Defaults to 5.
        
        Returns:
            list: Processed messages
        """
        try:
            # Fetch messages asynchronously
            messages = run_async(self._fetch_messages(limit))
            
            # Process each message
            processed_messages = []
            for message in messages:
                # Ensure message is a dictionary with text
                if isinstance(message, dict) and 'text' in message:
                    # Process the message (add to history, create task, notify)
                    task_id = handle_telegram_message(message)
                    
                    # Add to processed messages list
                    processed_messages.append(message)
            
            return processed_messages
        except Exception as e:
            log(f"Error in get_last_few_messages: {e}")
            log(traceback.format_exc())
            return []

    async def _fetch_messages(self, limit=5):
        """Async method to fetch messages from Telegram API."""
        try:
            # Ensure we have a fresh bot instance
            bot = Bot(token=self.api_key)
            
            log(f"Fetching updates with limit {limit}")
            
            # Get updates with a limit to control the number of messages
            updates = await bot.get_updates(limit=limit, timeout=1)
            
            log(f"Total updates received: {len(updates)}")
            
            # Log details of each update for debugging
            for update in updates:
                log(f"Update details: {update}")
                if update.message:
                    log(f"Message chat ID: {update.message.chat.id}")
                    log(f"Message text: {update.message.text}")
            
            # Filter messages for the specific chat
            messages = [
                update.message.to_dict() 
                for update in updates 
                if (update.message and 
                    update.message.chat and 
                    str(update.message.chat.id) == self.chat_id and 
                    update.message.text)
            ]
            
            log(f"Filtered messages: {messages}")
            return messages
        except Exception as e:
            log(f"Error in _fetch_messages: {e}")
            log(f"Traceback: {traceback.format_exc()}")
            return []

    def get_previous_message_history(self, limit=10):
        """Fetch previous message history from the Telegram API."""
        return self.get_last_few_messages(limit)

    def is_authorized_user(self, update: Update):
        """Check if the user is authorized to use the bot"""
        authorized = update.effective_user.id == int(self.chat_id)
        if not authorized:
            log(f"Unauthorized user: {update}")
            chat_id = update.message.chat.id
            run_async(self._send_unauthorized_message(chat_id))
        return authorized

    async def _send_unauthorized_message(self, chat_id):
        """Send an unauthorized message"""
        bot = Bot(token=self.api_key)
        await bot.send_message(
            chat_id=chat_id,
            text="You are not authorized to use this bot. Check out Auto-GPT-Plugins on GitHub: https://github.com/Significant-Gravitas/Auto-GPT-Plugins"
        )

from typing import Dict
from utils.task_tree import create_task_from_json

def is_message_a_task(message: Dict) -> bool:
    """
    Placeholder function to determine if a message represents a task.
    Currently always returns True.
    
    Args:
        message (Dict): Telegram message dictionary
    
    Returns:
        bool: Always True for now
    """
    return True

def handle_telegram_message(message: Dict):
    """
    Process a Telegram message by:
    1. Adding to conversation history
    2. Creating a task
    3. Notifying Telegram the message is read

    Args:
        message (Dict): Telegram message dictionary

    Returns:
        str or None: Created task ID or None
    """
    # Ensure message is a dictionary with text
    if not isinstance(message, dict) or 'text' not in message:
        log("Invalid message format")
        return None

    # Get Telegram utility instance
    telegram_utils = TelegramUtils.get_instance()
    if not telegram_utils:
        log("Failed to get Telegram utils instance")
        return None

    # 1. Add to conversation history
    telegram_utils.add_to_conversation_history(message)
    
    # Save to JSONL file
    conv_history_path = os.path.join(os.path.dirname(__file__), '..', 'conv_history.jsonl')
    with open(conv_history_path, 'a') as f:
        f.write(json.dumps(message) + '\n')

    # 2. Create task from message
    task_id = create_task_from_json({
        "title": f"Telegram Message: {message['text'][:50]}...",
        "description": f"Telegram message content:\n\n{message['text']}",
        "priority": 1,  # High priority for user messages
        "source": "telegram",
        "metadata": {
            "original_message": message
        }
    })

    # 3. Notify Telegram message is read
    telegram_utils.send_message(f"Message received and processed. Task ID: {task_id}")

    # Log the task creation
    log(f"Created task {task_id} for Telegram message: {message['text']}")

    return task_id

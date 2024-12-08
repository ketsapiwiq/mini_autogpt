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
        """Fetch the last few messages from conversation history."""
        return self.conversation_history[-limit:]

    def get_previous_message_history(self, limit=10):
        """Fetch previous message history."""
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

def handle_telegram_message(message: Dict) -> str:
    """
    Create a new task from an incoming Telegram message using JSON structure.
    Returns the created task ID
    """
    # Extract message content
    text = message.get("text", "")

    # Create high priority task for telegram messages
    task_data = {
        "title": f"Process Telegram message: {text[:50]}...",
        "description": f"Analyze and respond to Telegram message:\n\n{text}",
        "priority": 1,  # High priority for user messages
        "source": "telegram",
        "subtasks": []
    }

    task_id = create_task_from_json(task_data)

    return task_id

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

# Load environment variables from .env file
load_dotenv()

response_queue = ""

def run_async(coro):
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:  # 'RuntimeError: There is no current event loop...'
        loop = None
    if loop and loop.is_running():
        return loop.create_task(coro)
    else:
        if os.name == "nt":
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        return asyncio.run(coro)

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
        # Remove the exit(1) and replace with more flexible error handling
        if not api_key:
            log("No API key provided for Telegram.")
            return

        self.api_key = api_key
        self.chat_id = str(chat_id)  # Ensure chat_id is a string
        self.bot = None
        self.last_processed_update_id = None
        self._initialize_bot()

    def _initialize_bot(self):
        """Initialize the Telegram bot with proper error handling."""
        try:
            import telegram
            self.bot = telegram.Bot(token=self.api_key)
        except Exception as e:
            log(f"Error initializing Telegram bot: {e}")
            self.bot = None

    async def _get_bot(self):
        """Async method to get bot instance."""
        if not self.bot:
            self._initialize_bot()
        return self.bot

    def get_last_few_messages(self, limit=5):
        """Fetch the last few messages directly from the Telegram API."""
        try:
            # Use run_async to handle the async method
            updates = run_async(self._fetch_messages(limit))
            return updates
        except Exception as e:
            log(f"Error fetching messages from Telegram API: {e}")
            return []

    async def _fetch_messages(self, limit=5):
        """Async method to fetch messages from Telegram API."""
        bot = await self._get_bot()
        if not bot:
            log("Telegram bot not initialized")
            return []

        try:
            # Get updates with a limit to control the number of messages
            updates = await bot.get_updates(limit=limit, timeout=1)
            
            # Filter messages for the specific chat
            messages = [
                update.message.text 
                for update in updates 
                if (update.message and 
                    update.message.chat and 
                    str(update.message.chat.id) == self.chat_id and 
                    update.message.text)
            ]
            
            # Update the last processed update ID
            if updates:
                self.last_processed_update_id = updates[-1].update_id
            
            return messages
        except Exception as e:
            log(f"Error in _fetch_messages: {e}")
            return []

    async def _poll_updates(self):
        """
        Async method to poll for updates with improved error handling 
        and event loop management.
        """
        global response_queue
        try:
            bot = await self._get_bot()
            if not bot:
                log("Telegram bot not initialized")
                return None

            log("Getting updates...")

            # Get initial updates
            last_update = await bot.get_updates(timeout=10)
            
            # Initialize last_update_id
            last_update_id = last_update[-1].update_id if last_update else -1

            while True:
                try:
                    # Get new updates
                    updates = await bot.get_updates(offset=last_update_id + 1, timeout=30)
                    
                    for update in updates:
                        # Check authorization
                        if not self.is_authorized_user(update):
                            continue

                        # Process message
                        if update.message and update.message.text:
                            # Set response and add to conversation history
                            response_queue = update.message.text
                            self.add_to_conversation_history("User: " + response_queue)
                            return response_queue

                        # Update last_update_id
                        last_update_id = max(last_update_id, update.update_id)

                except asyncio.TimeoutError:
                    log("Telegram update polling timed out")
                    continue
                except Exception as e:
                    log(f"Error while polling updates: {e}")
                    # Wait a bit before retrying to avoid rapid error loops
                    await asyncio.sleep(5)

                # Prevent tight looping
                await asyncio.sleep(1)

        except Exception as e:
            log(f"Critical error in _poll_updates: {e}")
            return None

    def send_message(self, message):
        """Interface method for sending a message."""
        try:
            # Add to conversation history
            self.add_to_conversation_history("Sent: " + message)
            
            # Send message with ellipsis
            self._send_message(message + "...")
            return "Sent message successfully."
        except Exception as e:
            log(f"Error sending message: {e}")
            return f"Failed to send message: {e}"

    def ask_user(self, prompt):
        """Interface Method for Auto-GPT.
        Ask the user a question, return the answer"""
        max_attempts = 3
        for attempt in range(max_attempts):
            try:
                # Use run_async to handle the async method
                answer = run_async(self.ask_user_async(prompt=prompt))
                return answer
            except Exception as e:
                log(f"Telegram ask_user attempt {attempt + 1} failed: {e}")
                if attempt == max_attempts - 1:
                    return "User has not answered."
                # Wait a bit before retrying
                time.sleep(2)

    def add_to_conversation_history(self, message):
        """
        Send a message to the Telegram chat instead of saving to file.
        """
        try:
            run_async(self._send_message_async(message))
        except Exception as e:
            log(f"Error sending message to Telegram: {e}")

    def get_previous_message_history(self):
        """Fetch previous message history from the Telegram API."""
        return self.get_last_few_messages(limit=10)

    def is_authorized_user(self, update: Update):
        authorized = update.effective_user.id == int(self.chat_id)
        if not authorized:
            log("Unauthorized user: " + str(update))
            chat_id = update.message.chat.id
            temp_bot = Bot(self.api_key)
            temp_bot.send_message(
                chat_id=chat_id,
                text="You are not authorized to use this bot. Checkout Auto-GPT-Plugins on GitHub: https://github.com/Significant-Gravitas/Auto-GPT-Plugins",
            )
        return authorized

    def handle_response(self, update: Update, context: CallbackContext):
        try:
            log("Received response: " + update.message.text)

            if self.is_authorized_user(update):
                response_queue.put(update.message.text)
        except Exception as e:
            log(e)

    async def get_bot(self):
        bot_token = self.api_key
        bot = Bot(token=bot_token)
        # commands = await bot.get_my_commands()
        # if len(commands) == 0:
        #     await self.set_commands(bot)
        return bot

    def _send_message(self, message, speak=False):
        try:
            run_async(self._send_message_async(message=message))
            if speak:
                self._speech(message)
        except Exception as e:
            log(f"Error while sending message: {e}")
            return "Error while sending message."

    async def _send_message_async(self, message, speak=False):
        log("Sending message on Telegram: " + str(message))
        recipient_chat_id = self.chat_id
        bot = await self.get_bot()

        # properly handle messages with more than 2000 characters by chunking them
        if len(message) > 2000:
            message_chunks = [
                message[i : i + 2000] for i in range(0, len(message), 2000)
            ]
            for message_chunk in message_chunks:
                await bot.send_message(chat_id=recipient_chat_id, text=message_chunk)
        else:
            await bot.send_message(chat_id=recipient_chat_id, text=message)
        if speak:
            await self._speech(message)

    async def ask_user_async(self, prompt, speak=False):
        global response_queue

        response_queue = ""
        # await delete_old_messages()

        log("Asking user: " + prompt)
        await self._send_message_async(message=prompt, speak=speak)

        self.add_to_conversation_history("AI: " + prompt)
        log("Waiting for response on Telegram chat...")
        await self._poll_updates()

        response_text = response_queue

        log("Response received from Telegram: " + response_text)
        return response_text

    def poll_anyMessage(self):
        print("Waiting for first message...")
        return run_async(self.poll_anyMessage_async())

    async def poll_anyMessage_async(self):
        bot = Bot(token=self.api_key)
        last_update = await bot.get_updates(timeout=30)
        if len(last_update) > 0:
            last_update_id = last_update[-1].update_id
        else:
            last_update_id = -1

        while True:
            try:
                log("Waiting for first message...")
                updates = await bot.get_updates(offset=last_update_id + 1, timeout=30)
                for update in updates:
                    if update.message:
                        return update
            except Exception as e:
                log(f"Error while polling updates: {e}")

            await asyncio.sleep(1)

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

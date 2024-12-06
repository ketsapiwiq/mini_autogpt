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
        self.chat_id = chat_id
        self.load_conversation_history()

    def get_last_few_messages(self):
        """Interface method. Get the last few messages."""
        try:
            # Ensure conversation history is loaded
            self.load_conversation_history()
            
            # Log the total number of messages in conversation history
            log(f"Total messages in conversation history: {len(self.conversation_history)}")
            
            # Return last 10 messages or all if less than 10
            last_messages = self.conversation_history[-10:]
            
            # Log details about retrieved messages
            log(f"Retrieving last {len(last_messages)} messages")
            for idx, msg in enumerate(last_messages, 1):
                log(f"Message {idx}: {msg}")
            
            return last_messages
        except Exception as e:
            log(f"Error retrieving last messages: {e}")
            log(traceback.format_exc())
            return []

    def get_previous_message_history(self):
        """Interface method. Get the previous message history."""
        try:
            if len(self.conversation_history) == 0:
                return "There is no previous message history."

            tokens = 0
            if tokens > 1000:
                log("Message history is over 1000 tokens. Summarizing...")
                chunks = []
                summaries = []
                summarized_history = " ".join(summaries)
                return summarized_history

            return self.conversation_history
        except Exception as e:
            log(f"Error while getting previous message history: {e}")
            log(traceback.format_exc())
            exit(1)

    def load_conversation_history(self):
        """Load the conversation history from a file."""
        try:
            # Log the current working directory to help with file path debugging
            log(f"Current working directory: {os.getcwd()}")
            
            # Attempt to load conversation history
            with open("conversation_history.json", "r") as f:
                self.conversation_history = json.load(f)
            
            # Log details about loaded conversation history
            log(f"Loaded {len(self.conversation_history)} messages from conversation_history.json")
        except FileNotFoundError:
            # If the file doesn't exist, create it.
            log("conversation_history.json not found. Creating empty conversation history.")
            self.conversation_history = []
        except json.JSONDecodeError:
            # Handle potential JSON decoding errors
            log("Error decoding conversation_history.json. Creating empty conversation history.")
            self.conversation_history = []
        except Exception as e:
            # Catch any other unexpected errors
            log(f"Unexpected error loading conversation history: {e}")
            log(traceback.format_exc())
            self.conversation_history = []

    def save_conversation_history(self):
        """Save the conversation history to a file."""
        with open("conversation_history.json", "w") as f:
            json.dump(self.conversation_history, f)

    def add_to_conversation_history(self, message):
        """Add a message to the conversation history and save it."""
        self.conversation_history.append(message)
        self.save_conversation_history()

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

    async def _poll_updates(self):
        global response_queue
        bot = await self.get_bot()
        log("getting updates...")

        last_update = await bot.get_updates(timeout=10)
        if len(last_update) > 0:
            last_messages = []
            for u in last_update:
                if not self.is_authorized_user(u):
                    continue
                if u.message and u.message.text:
                    last_messages.append(u.message.text)
                else:
                    log("no text in message in update: " + str(u))
            last_messages = []
            for u in last_update:
                if not self.is_authorized_user(u):
                    continue
                if u.message:
                    if u.message.text:
                        last_messages.append(u.message.text)
                    else:
                        log("no text in message in update: " + str(u))
            # itarate and check if last messages are already known, if not add to history
            for message in last_messages:
                self.add_to_conversation_history("User: " + message)

            log("last messages: " + str(last_messages))
            last_update_id = last_update[-1].update_id

        else:
            last_update_id = -11

        log("last update id: " + str(last_update_id))
        log("Waiting for new messages...")
        while True:
            try:
                updates = await bot.get_updates(offset=last_update_id + 1, timeout=30)
                for update in updates:
                    if self.is_authorized_user(update):
                        if update.message and update.message.text:
                            response_queue = update.message.text
                            self.add_to_conversation_history("User: " + response_queue)
                            return response_queue

                    last_update_id = max(last_update_id, update.update_id)
            except TimedOut:
                continue
            except Exception as e:
                log(f"Error while polling updates: {e}")

            await asyncio.sleep(1)

    def send_message(self, message):
        """Interface method for sending a message."""
        self.add_to_conversation_history("Sent: " + message)
        self._send_message(message + "...")
        return "Sent message successfully."

    def ask_user(self, prompt):
        """Interface Method for Auto-GPT.
        Ask the user a question, return the answer"""
        answer = "User has not answered."
        try:
            answer = run_async(self.ask_user_async(prompt=prompt))
        except TimedOut:
            log("Telegram timeout error, trying again...")
            answer = self.ask_user(prompt=prompt)
        return answer

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

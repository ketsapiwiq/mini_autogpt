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
from autogen import Agent, AssistantAgent, UserProxyAgent, config_list_from_json
from guidance import models
import re
from action.tasks import task_manager

def is_message_a_task(message: Dict) -> bool:
    """
    Determine if a Telegram message represents a task using an Autogen agent.
    
    Args:
        message (Dict): Telegram message dictionary
    
    Returns:
        bool: True if the message appears to be a task, False otherwise
    """
    try:
        # Extract the message text
        message_text = message.get('text', '')
        
        # If message is empty, it's not a task
        if not message_text:
            return False
        
        # Load Autogen configuration
        llm_config = config_list_from_json("OAI_CONFIG_LIST")[0]
        
        # Create an assistant agent to evaluate the message
        task_classifier = AssistantAgent(
            "task_classifier", 
            system_message="You are an expert at identifying tasks from text messages. "
                           "Respond with 'yes' if the message describes a task to be done, "
                           "or 'no' if it does not.",
            llm_config=llm_config
        )
        
        # Create a user proxy agent to initiate the conversation
        user_proxy = UserProxyAgent(
            "user_proxy", 
            human_input_mode="TERMINATE",
            max_consecutive_auto_reply=1
        )
        
        # Store the task classification result
        task_classification = [None]
        
        def is_task_message(recipient, messages, sender, config):
            # Use the last message for classification
            last_message = messages[-1]['content']
            
            # Classify the message
            task_classification[0] = 'yes' in last_message.lower()
            return True, "Task classification complete."
        
        # Register the custom reply function
        task_classifier.register_reply(Agent, is_task_message, 1)
        
        # Initiate the chat to classify the message
        user_proxy.initiate_chat(
            task_classifier, 
            message=f"Is the following message a task that needs to be done? Message: '{message_text}'"
        )
        
        # Return the classification result
        return task_classification[0] or False
    
    except Exception as e:
        log(f"Error classifying task message: {e}")
        # If there's an error, default to treating it as a task
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
    # Add message to conversation history
    telegram_utils = TelegramUtils.get_instance()
    if telegram_utils:
        telegram_utils.add_to_conversation_history(f"Received: {message.get('text', '')}")

    # Check if the message is a task
    if is_message_a_task(message):
        # Prepare task details
        task_details = {
            'title': f"Telegram Message: {message.get('text', '')[:50]}...",
            'description': message.get('text', ''),
            'source': 'telegram',
            'status': 'in_progress',
            'priority': 1,  # High priority for user messages
            'metadata': {
                'original_message': message
            }
        }

        # Create task and get task ID
        task_id = task_manager.create_task(task_details)

        # Notify Telegram message is read
        telegram_utils.send_message(f"Message received and processed. Task ID: {task_id}")

        log(f"Created task {task_id} for Telegram message: {message.get('text', '')}")

        return task_id

    return None

def telegram_task_commands(update: Update, context: CallbackContext):
    """
    Handle Telegram bot commands related to task management.
    
    Commands:
    - /tasks: List active tasks
    - /task_history: Show task history
    - /cancel_task <task_id>: Cancel a specific task
    - /pause_task <task_id>: Pause a specific task
    """
    command = update.message.text.split()[0]
    args = update.message.text.split()[1:] if len(update.message.text.split()) > 1 else []
    
    telegram_utils = TelegramUtils.get_instance()
    if not telegram_utils:
        return

    if command == '/tasks':
        active_tasks = task_manager.get_active_tasks()
        if active_tasks:
            response = "🔧 Active Tasks:\n"
            for task in active_tasks:
                response += (f"Task ID: {task['id']}\n"
                             f"Title: {task.get('title', 'No title')}\n"
                             f"Status: {task['status']}\n"
                             f"Description: {task.get('description', 'No description')}\n\n")
        else:
            response = "No active tasks at the moment."
        
        telegram_utils.send_message(response)

    elif command == '/task_history':
        task_history = task_manager.get_task_history()
        if task_history:
            response = "📋 Task History:\n"
            for task in task_history[-10:]:  # Show last 10 tasks
                response += (f"Task ID: {task['id']}\n"
                             f"Title: {task.get('title', 'No title')}\n"
                             f"Status: {task['status']}\n"
                             f"Description: {task.get('description', 'No description')}\n\n")
        else:
            response = "No task history available."
        
        telegram_utils.send_message(response)

    elif command == '/cancel_task':
        if not args:
            telegram_utils.send_message("Please provide a task ID to cancel.")
            return
        
        task_id = args[0]
        task_manager.cancel_task(task_id)
        telegram_utils.send_message(f"Task {task_id} has been cancelled.")

    elif command == '/pause_task':
        if not args:
            telegram_utils.send_message("Please provide a task ID to pause.")
            return
        
        task_id = args[0]
        task_manager.pause_task(task_id)
        telegram_utils.send_message(f"Task {task_id} has been paused.")

"""User interaction commands."""
from typing import Dict, Any
from . import Command
from utils.simple_telegram import TelegramUtils
from utils.log import log
import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

class SendMessageCommand(Command):
    """Command to send a message to the user via Telegram.
    
    This command sends a one-way message to the user without expecting a response.
    Use this for notifications, updates, or sharing information.
    
    Arguments:
        message (str): The message to send to the user. Should be clear and concise.
    
    Returns:
        Dict containing:
        - status: "success" or "error"
        - message: Confirmation of message sent
    """
    
    def validate_args(self, args: Dict[str, Any]) -> bool:
        return isinstance(args.get("message"), str)
    
    def get_args(self) -> Dict[str, str]:
        return {
            "message": "The message to send to the user. Should be clear and concise."
        }
    
    def execute(self, args: Dict[str, Any]) -> Dict[str, Any]:
        message = args["message"]
        telegram = TelegramUtils.get_instance(
            api_key=os.getenv("TELEGRAM_API_KEY"),
            chat_id=os.getenv("TELEGRAM_CHAT_ID")
        )
        telegram.send_message(message)
        return {"status": "success", "message": "Message sent"}

class AskUserCommand(Command):
    """Command to ask the user a question and wait for their response via Telegram.
    
    This command sends a message to the user and waits for their reply.
    Use this when you need user input, confirmation, or clarification.
    
    Arguments:
        message (str): The question or prompt to send to the user. Should be clear and specific.
    
    Returns:
        Dict containing:
        - status: "success" or "debug"
        - response: The user's response text
    """
    
    def validate_args(self, args: Dict[str, Any]) -> bool:
        return isinstance(args.get("message"), str)
    
    def get_args(self) -> Dict[str, str]:
        return {
            "message": "The question or prompt to send to the user. Should be clear and specific."
        }
    
    def execute(self, args: Dict[str, Any]) -> Dict[str, Any]:
        message = args["message"]
        telegram = TelegramUtils.get_instance(
            api_key=os.getenv("TELEGRAM_API_KEY"),
            chat_id=os.getenv("TELEGRAM_CHAT_ID")
        )
        response = telegram.ask_user(message)
        
        if response == "/debug":
            log("Debug command received")
            return {"status": "debug", "response": response}
            
        return {"status": "success", "response": response}

class TellUserCommand(Command):
    """Command to tell something to the user without interaction.
    
    This command is used to output information to the user without expecting a response.
    It's a non-interactive way to communicate information.
    
    Arguments:
        message (str): The message to tell the user. Should be clear and informative.
    
    Returns:
        Dict containing:
        - status: "success"
        - message: Confirmation that the message was delivered
    """
    
    def validate_args(self, args: Dict[str, Any]) -> bool:
        return isinstance(args.get("message"), str)
    
    def get_args(self) -> Dict[str, str]:
        return {
            "message": "The message to tell the user. Should be clear and informative."
        }
    
    def execute(self, args: Dict[str, Any]) -> Dict[str, Any]:
        message = args["message"]
        log(f"[TELL USER] {message}")
        return {"status": "success", "message": "Information delivered to user"}

# Register commands
from .registry import CommandRegistry
CommandRegistry.register("send_message", SendMessageCommand)
CommandRegistry.register("ask_user", AskUserCommand)
CommandRegistry.register("tell_user", TellUserCommand)

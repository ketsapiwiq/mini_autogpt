import json
import time
import traceback
from utils.log import log, debug
from utils.simple_telegram import TelegramUtils
import think.memory as memory
from utils.web_search import web_search
from utils.error_handling import ErrorCounter

from itertools import islice
from duckduckgo_search import DDGS
import os

from dotenv import load_dotenv

COMMAND_CATEGORY = "web_search"
COMMAND_CATEGORY_TITLE = "Web Search"

DUCKDUCKGO_MAX_ATTEMPTS = 3


def take_action(command):
    """Execute a command based on the AI's decision."""
    from action.commands.registry import CommandRegistry
    
    load_dotenv()

    try:
        # Ensure command is a dictionary
        if isinstance(command, str):
            try:
                command = json.loads(command)
            except json.JSONDecodeError:
                log("Failed to parse command as JSON")
                return

        if not isinstance(command, dict):
            log(f"Command is not a dictionary: {type(command)}")
            return

        action = command.get("command", {}).get("name")
        args = command.get("command", {}).get("args", {})

        if not action:
            log("No valid action found in command")
            return

        debug(f"Executing Action:\nCommand: {action}\nArguments: {json.dumps(args, indent=2)}")
        
        try:
            # Log available commands for debugging
            available_commands = CommandRegistry.get_available_commands()
            debug("Available Commands during execution:")
            for cmd in available_commands:
                debug(f"- {cmd['name']}: {cmd['description']}")
            
            result = CommandRegistry.execute(action, args)
            debug(f"Action Result:\n{json.dumps(result, indent=2)}")
            
            memory.add_to_response_history(
                str(command),
                str(result)
            )
            log("Command executed successfully")
            
            if ErrorCounter.get_count() > 0:
                ErrorCounter.reset()
                
        except ValueError as e:
            log(f"Command execution failed: {e}")
            return
            
    except Exception as e:
        log("ERROR WITHIN JSON RESPONSE!")
        log(e)
        log(traceback.format_exc())
        log("Faulty message start:")
        log(command)
        log("end of faulty message.")
        log("END OF ERROR WITHIN JSON RESPONSE!")


def safe_google_results(results: str | list):
    if isinstance(results, list):
        safe_message = json.dumps(
            [result.encode("utf-8", "ignore").decode("utf-8") for result in results]
        )
    else:
        safe_message = results.encode("utf-8", "ignore").decode("utf-8")
    return safe_message

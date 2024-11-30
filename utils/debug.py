"""Utilities for colored debug output."""
from colorama import Fore, Back, Style
import json

def debug_prompt(prompt: str, title: str = "PROMPT"):
    """Print a prompt with colored formatting for better visibility.
    
    Args:
        prompt: The prompt text to display
        title: Optional title for the debug section
    """
    print(f"\n{Fore.CYAN}{'='*20} {title} {'='*20}{Style.RESET_ALL}")
    print(f"{Fore.GREEN}{prompt}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*50}{Style.RESET_ALL}\n")

def debug_json(data: dict, title: str = "JSON"):
    """Print JSON data with colored formatting and proper indentation.
    
    Args:
        data: Dictionary to display as JSON
        title: Optional title for the debug section
    """
    formatted_json = json.dumps(data, indent=2)
    print(f"\n{Fore.YELLOW}{'='*20} {title} {'='*20}{Style.RESET_ALL}")
    print(f"{Fore.MAGENTA}{formatted_json}{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}{'='*50}{Style.RESET_ALL}\n")

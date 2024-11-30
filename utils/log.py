import json
import sys
import os
from datetime import datetime
from colorama import init, Fore, Style

init(autoreset=True)  # Initialize colorama with autoreset

DEBUG = True  # Set to True to enable debug logging

def log(message, end="\n", flush=True):
    """Log a message to stdout."""
    if DEBUG:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        print(f"{Fore.GREEN}[{timestamp}]{Style.RESET_ALL} {message}", end=end, flush=flush)
    else:
        print(message, end=end, flush=flush)

def debug(message):
    """Log a debug message if DEBUG is enabled."""
    if DEBUG:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        print(f"{Fore.BLUE}[DEBUG {timestamp}]{Style.RESET_ALL} {message}", flush=True)

def error(message):
    """Log an error message."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    print(f"{Fore.RED}[ERROR {timestamp}]{Style.RESET_ALL} {message}", flush=True)

def warning(message):
    """Log a warning message."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    print(f"{Fore.YELLOW}[WARNING {timestamp}]{Style.RESET_ALL} {message}", flush=True)

def save_debug(message, filename="debug.log", response=None):
    """Save a debug message to a file. Optionally include a response."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    with open(filename, "a") as f:
        f.write(f"[{timestamp}] {message}\n")
        if response:
            f.write(f"Response: {response}\n")

def save_debug_data(data, response):
    """Save the debug to a file."""
    with open("debug_data.json", "w") as f:
        json.dump(data, f)
    with open("debug_response.json", "w") as f:
        json.dump(response, f)

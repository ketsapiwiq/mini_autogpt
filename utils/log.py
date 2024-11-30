import json
import sys
import os
from datetime import datetime

DEBUG = True  # Set to True to enable debug logging

def log(message, end="\n", flush=True):
    """Log a message to stdout."""
    if DEBUG:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        print(f"[{timestamp}] {message}", end=end, flush=flush)
    else:
        print(message, end=end, flush=flush)

def debug(message):
    """Log a debug message if DEBUG is enabled."""
    if DEBUG:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        print(f"[DEBUG {timestamp}] {message}", flush=True)

def save_debug(message, filename="debug.log"):
    """Save a debug message to a file."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    with open(filename, "a") as f:
        f.write(f"[{timestamp}] {message}\n")

def save_debug_data(data, response):
    """Save the debug to a file."""
    with open("debug_data.json", "w") as f:
        json.dump(data, f)
    with open("debug_response.json", "w") as f:
        json.dump(response, f)

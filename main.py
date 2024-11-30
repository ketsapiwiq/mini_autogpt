"""Main entry point for mini_autogpt."""
import sys
from pathlib import Path
import traceback
sys.path.append(str(Path(__file__).parent))
from think.think import process_thoughts
from utils.log import log
import time

def main():
    """Run the main AI loop."""
    log("*** I am thinking... ***")
    while True:
        try:
            process_thoughts()
            time.sleep(1)
        except KeyboardInterrupt:
            print("Shutting down...")
            break
        except Exception as e:
            print(f"Error in main loop: {str(e)}")
            print(f"Full traceback: {traceback.format_exc()}")
            time.sleep(5)

def write_start_message():
    """Display the startup ASCII art."""
    ascii_art = """                           
                                                 
                         ░▓█▓░░                          
         ▒▒▒      ██░ ░░░░░░░░░░ ░░██░      ▒░           
         ▒▒▒░ ░█░░▒░░░░░░░░░     ░░░▒ ░█   ░▒░░          
      ▒░    ░█ ▒▒░░░░░░░░░░░░░░░░░▒▒▒ █      ░▒       
     ░▒▒░  ▒░▒▒▒░███░░░░░░░░░░░░░░░███░▒▒░▓░  ▒▒▒░▒▒     
      ░   ▒░▒▒▒░░░░░░░░░░░░░░░░░░░░░░░░░▒▒▒░    ░▒       
          █▒▒░░██░░░▒░░░░░░░░░░░░░░░░░██░░▒▒█            
   ▒░░▒  █░▒▒░█░█▓░   █░░░░░░░░░█   █▒█░█░▒▒░░           
         █░▒▒█░████   ██░░░░░░░██  ░████░█▒▒░█  ▒░░▒     
         █░▒▒█ █▓░░█▒░▓█░█░░▓▓░█▓░██░█▓█ ▒▒▒░░    ░      
         ░█▒▒▒░ ▓░░░░░█░░░▒▒▒░░░█░░░░▓░ ░▒▒░█            
    ░█░█░ ░█▒▒▒▓▒░▒░░░░░░░░░░░░░░░░░▒▓▓▒▒▒░█  ▒░░█░      
   █░░░█    █░▒▒▒▒▒▒▒▒▒░░░░░░░░░░▒▒▒▒▒▒▒▒░█   ░█░░░█     
   █▓▒░░ ████▓██▒▒▓▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▓▒▒██▓████░░░▒▓█     
   █▒▒▓▒░▒▒▒▒▓█▓▒▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▒▓█▒▒▒▒▒░▒▓▓▒▓     
    ▓▒██░░   ░░░░░░▓▓▒░░░░▓▓▓░░░░▒▓▓░░░░░░    ░██▒░      
    █░░░░░░░░░░░░▒▓█░▒░░░░▒▓▒░░░░▒░█▓░░░░░░░░░░░░░█      
    █▓░░▓▓▒▒▒█░░░░░█░░░░░▒▓▓▓▒░░░░░░█░░░░░█▒▒▒▒▓░░▒█      
     ███░░▓▓█▒▓▒▒░░░░░▒▒▓▒█▓▓▒░░░░░░▒▒▓▓▒▓▓▓░░▓██       
     ░░░█████▓▒░▒▒░▒▒▒▒▒▒▒█░█▓▒▒▒▒▒▒▒▒▓▒░██████░░░       
      ░░░░░░░░██░░█▓░▒▒░█░░░░░█░█░░█▒░▒█"""
    print(ascii_art)
    message = """Hello my friend!
I am Mini-Autogpt, a small version of Autogpt for smaller llms.
I am here to help you and will try to contact you as soon as possible!

Note: I am still in development, so please be patient with me! <3

"""
    for char in message:
        print(char, end="", flush=True)

if __name__ == "__main__":
    main()

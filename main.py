"""Main entry point for mini_autogpt."""
import think.think as think
from utils.log import log
import time

def main():
    """Run the main AI loop."""
    write_start_message()
    while True:
        try:
            think.run_think()
            time.sleep(1)
        except KeyboardInterrupt:
            log("Shutting down...")
            break
        except Exception as e:
            log(f"Error in main loop: {e}")
            time.sleep(5)

def write_start_message():
    """Display the startup ASCII art."""
    ascii_art = """                           
                                                 
                         ░▓█▓░░                          
         ▒▒▒      ██░ ░░░░░░░░░░ ░░██░      ▒░           
         ▒▒▒░ ░█░░▒░░░░░░░░░     ░░░▒ ░█   ░▒░░          
      ▒░    ░█ ▒▒░░░░░░░░░░░░░░░░░░░░▒▒▒ █      ░▒       
     ░▒▒░  ▒░▒▒▒░███░░░░░░░░░░░░░░░███░▒▒░▓░  ▒▒▒░▒▒     
      ░   ▒░▒▒▒░░░░░░░░░░░░░░░░░░░░░░░░░▒▒▒░    ░▒       
          █▒▒░░██░░░▒░░░░░░░░░░░░░░░░░██░░▒▒█            
   ▒░░▒  █░▒▒░█░█▓░   █░░░░░░░░░█   █▒█░█░▒▒░░           
         █░▒▒█░████   ██░░░░░░░██  ░████░█▒▒░█  ▒░░▒     
         █░▒▒█ █▓░░█▒░▓█░█░░▓▓░█▓░██░█▓█ ▒▒▒░░    ░      
         ░█▒▒▒░ ▓░░░░░█░░░▒▒▒░░░█░░░░▓░ ░▒▒░█            
    ░█░█░ ░█▒▒▒▓▒░▒░░░░░░░░░░░░░░░░░▒▓▓▒▒▒░█  ▒░░█░      
   █░░░█    █░▒▒▒▒▒▒▒▒▒░░░░░░░░░░▒▒▒▒▒▒▒▒░█   ░█░░░█     
   █▓▒░░ ████▓██▒▒▓▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▓▒▒██▓████░░░▒▓█     
   █▒▒▓▒░▒▒▒▒▓█▓▒▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▒▓█▒▒▒▒▒░▒▓▓▒▓     
    ▓▒██░░   ░░░░░░▓▓▒░░░░▓▓▓░░░░▒▓▓░░░░░░    ░██▒░      
    █░░░░░░░░░░░░▒▓█░▒░░░░▒▓▒░░░░▒░█▓░░░░░░░░░░░░░█      
    █▓░░▓▓▒▒▒█░░░░░█░░░░░▒▓▓▓▒░░░░░█░░░░░█▒▒▒▒▓░░▒█      
     ███░░▓▓█▒▓▒▒▒░░░░░▒▒▓▒█▓▓▒░░░░░░▒▒▓▓▒▓▓▓░░▓██       
     ░░░█████▓▒░▒▒░▒▒▒▒▒▒▒█░█▓▒▒▒▒▒▒▒▒▓▒░██████░░░       
      ░░░░░░░░██░░█▓░▒▒░█░░░░░█░█░░█▒░▒█"""
    log(ascii_art)
    message = """Hello my friend!
I am Mini-Autogpt, a small version of Autogpt for smaller llms.
I am here to help you and will try to contact you as soon as possible!

Note: I am still in development, so please be patient with me! <3

"""
    for char in message:
        log(char, end="", flush=True)

if __name__ == "__main__":
    main()

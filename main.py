import think.think as think
import think.memory as memory
import json
import utils.llm as llm
# this is a test for using history from sophie_chat instead of the message history.

# feedback: It kindda works. But for some reason the llm starts repeating my input
# maybe having it structured like "plan:..." "context: summarized history" and "last few messages: ..." makes more sense?


def log(message):
    # print with white color
    print("\033[0m" + str(message) + "\033[0m")


def write_start_message():
    pic = """                           
                                                 
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
      ░░░░░░░░██░░█▓░▒▒░█░░░░░█░█░░█▒░▒██░░░░░░░         
             ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░                             
              
"""
    message = """Hello my friend!
I am Mini-Autogpt, a small version of Autogpt for smaller llms.
I am here to help you and will try to contact you as soon as possible!

Note: I am still in development, so please be patient with me! <3

"""
    # write the pic in print line by line with a tiny delay between each line, then add the message below as if someone was typing it.
    for line in pic.split("\n"):
        print(line)
        # time.sleep(0.1)
    for char in message:
        print(char, end="", flush=True)
        # time.sleep(0.05)


def start_mini_autogpt():
    write_start_message()

    # delete thoughts from memory
    # memory.forget_everything()

    base_prompt = "I want my AI to code new agent modules for me (browse web, run docker code, etc.).",
    # {
    #     "role": "user",
    #     "content": "I want my AI to code new agent modules for me (browse web, run docker code, etc.).",
    # }
    history = llm.build_prompt(base_prompt)

    thought_history = memory.load_thought_history()
    thought_summaries = [json.loads(item)["summary"] for item in thought_history]

    history = llm.build_context(
        history=history,
        conversation_history=thought_summaries,
        message_history=memory.load_response_history()[-2:],
        # conversation_history=telegram.get_previous_message_history(),
        # message_history=telegram.get_last_few_messages(),
    )
    # history = llm.build_prompt(prompt.thought_prompt)

    # run the main loop, nothing more to do in main.py
    while True:
        think.run_think(history)
        input()


if __name__ == "__main__":
    fail_counter = 0
    start_mini_autogpt()()

# dicisions based on thinking
# takes in thoughts and calls llm to make a decision on actions.
# takes summary of context

import json
import traceback
import utils.llm as llm
from utils.log import log
import think.prompt as prompt
import think.memory as memory
from utils.log import save_debug
from utils.error_handling import ErrorCounter


def extract_decision(thinking):
    return decide(thinking)


def decide(thoughts):
    log("deciding what to do...")
    history = []
    history.append({"role": "system", "content": prompt.action_prompt})

    # Only load conversation history if thoughts indicate a need for context
    if "previous" in thoughts.lower() or "context" in thoughts.lower():
        history = llm.build_context(
            history=history,
            conversation_history=memory.get_response_history(),
            message_history=memory.load_response_history()[-2:],
        )
    
    history.append({"role": "user", "content": "Thoughts: \n" + thoughts})
    history.append(
        {
            "role": "user",
            "content": "Determine exactly one command to use, and respond using the JSON schema specified previously:",
        },
    )

    response = llm.llm_request(history)
    log("finished deciding!")

    # Response is now directly the text content
    if not validate_json(response):
        response = extract_json_from_response(response)
        
    if not validate_json(response):
        ErrorCounter.increment()
        if ErrorCounter.should_exit():
            log("Got too many bad quality responses!")
            exit(1)
        save_debug(history, response=response)
        log("Retry Decision as faulty JSON!")
        return decide(thoughts)

    return response


def validate_json(test_response):
    try:
        if test_response is None:
            log("received empty json?")
            return False

        if isinstance(test_response, dict):
            response = test_response
        elif isinstance(test_response, str):
            response = json.loads(test_response)
        else:
            response = json.JSONDecoder().decode(test_response)

        # Only validate the command structure according to schema
        if "command" not in response:
            log("missing command field")
            return False
            
        command = response["command"]
        if not isinstance(command, dict):
            log("command must be an object")
            return False
            
        if "name" not in command or not isinstance(command["name"], str):
            log("command must have a name field that is a string")
            return False
            
        if "args" not in command or not isinstance(command["args"], dict):
            log("command must have an args field that is an object")
            return False

        return True
    except Exception as e:
        log(e)
        return False


def extract_json_from_response(response_text):
    # Find the index of the first opening brace and the last closing brace
    start_index = response_text.find("{")
    end_index = response_text.rfind("}")

    if start_index != -1 and end_index != -1 and end_index > start_index:
        json_str = response_text[start_index : end_index + 1]
        try:
            # Parse the JSON string
            parsed_json = json.loads(json_str)
            # Pretty print the parsed JSON
            log(json.dumps(parsed_json, indent=4, ensure_ascii=False))
            return parsed_json
        except json.JSONDecodeError as e:
            log(f"Error parsing JSON: {e}")
    else:
        log("No valid JSON found in the response.")

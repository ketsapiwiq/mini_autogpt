import openai
import os
from dotenv import load_dotenv
from utils.log import log, debug
import json
import traceback
import ollama

def one_shot_request(prompt, system_context):
    history = []
    history.append({"role": "system", "content": system_context})
    history.append({"role": "user", "content": prompt})
    response = llm_request(history)
    if response is not None:
        return response
    else:
        log("Error in one_shot_request")
        return None

def test_function_calling_support():
    """Test if Ollama supports function calling."""
    try:
        # Simple test function
        def add_numbers(a: int, b: int) -> int:
            return a + b

        response = ollama.chat(
            model='llama2',  # Use default model
            messages=[{'role': 'user', 'content': 'What is 2 + 2?'}],
            tools=[add_numbers],
        )
        
        # Check if response has tool_calls attribute and it works as expected
        if hasattr(response.message, 'tool_calls') and response.message.tool_calls:
            return True
        return False
    except Exception as e:
        debug(f"Function calling test failed: {str(e)}")
        return False

def llm_request_with_functions(history, available_functions=None):
    """
    Sends a request to Ollama with function calling support.
    """
    load_dotenv()
    model = os.getenv("MODEL", "llama2").split('#')[0].strip()
    
    try:
        response = ollama.chat(
            model=model,
            messages=history,
            tools=list(available_functions.values()) if available_functions else None,
        )

        # Handle function calls if present
        if hasattr(response.message, 'tool_calls') and response.message.tool_calls:
            for tool in response.message.tool_calls:
                function_to_call = available_functions.get(tool.function.name)
                if function_to_call:
                    result = function_to_call(**tool.function.arguments)
                    # Add function result to conversation
                    history.append({
                        'role': 'function',
                        'name': tool.function.name,
                        'content': str(result)
                    })
            
            # Get final response after function calls
            final_response = ollama.chat(model=model, messages=history)
            return final_response.message.content
        
        return response.message.content
    except Exception as e:
        debug(f"Error in llm_request_with_functions: {str(e)}")
        return None

def llm_request(history, available_functions=None):
    """
    Sends a request to the LLM API, attempting to use function calling if supported.
    Falls back to standard chat completion if not supported.
    """
    debug("Starting LLM request")
    
    # Test for function calling support if functions are provided
    if available_functions and test_function_calling_support():
        debug("Using Ollama function calling")
        return llm_request_with_functions(history, available_functions)
    
    # Fall back to standard chat completion
    debug("Using standard chat completion")
    load_dotenv()
    # Strip any comments and whitespace from environment variables
    model = os.getenv("MODEL", "llama3.1:8b-instruct-q8_0").split('#')[0].strip()
    temperature = float(os.getenv("TEMPERATURE", "0.7").split('#')[0].strip())
    max_tokens = int(os.getenv("MAX_TOKENS", "1024").split('#')[0].strip())
    api_url = os.getenv("API_URL", "http://localhost:11434/v1").split('#')[0].strip()

    debug(f"Using model: {model}")
    debug(f"API URL: {api_url}")
    debug(f"Temperature: {temperature}")
    debug(f"Max tokens: {max_tokens}")

    try:
        debug("Initializing OpenAI client")
        # Initialize OpenAI-compatible client
        client = openai.OpenAI(
            api_key=os.getenv("OPENAI_API_KEY") or "test",
            base_url=api_url,
        )

        log(f"Attempting request with MODEL={model} to URL={api_url}")
        
        # Ensure proper message format
        formatted_history = []
        for msg in history:
            if isinstance(msg, dict) and 'role' in msg and 'content' in msg:
                # If content is a dict, convert it to string
                if isinstance(msg['content'], dict):
                    msg['content'] = str(msg['content'])
                formatted_history.append(msg)
            elif isinstance(msg, str):
                # If message is a string, assume it's user content
                formatted_history.append({"role": "user", "content": msg})
            else:
                debug(f"Skipping invalid message format: {msg}")

        log("Request history: " + str(formatted_history))

        debug("Sending request to API")
        # Send the request with streaming enabled
        response = client.chat.completions.create(
            model=model,
            messages=formatted_history,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=True
        )
        debug("Got initial streaming response")

        # Process the streaming response
        collected_messages = []
        debug("Starting to process stream")
        for chunk in response:
            # debug(f"Received chunk: {chunk}")
            if chunk.choices[0].delta.content is not None:
                content = chunk.choices[0].delta.content
                collected_messages.append(content)
                print(content, end='', flush=True)  # Print in real-time
        print()  # New line after all chunks

        # Join all collected messages into a single string
        full_response = ''.join(collected_messages)
        debug(f"Full response: {full_response}")
        return full_response

    except Exception as e:
        debug(f"Error in llm_request: {str(e)}")
        debug(f"Full traceback: {traceback.format_exc()}")
        return None

def build_context(history, conversation_history, message_history):
    """Build context for the LLM request from various history sources."""
    if conversation_history:
        history.extend(conversation_history)
    if message_history:
        for msg in message_history:
            history.append({"role": "user", "content": msg})
    return history

def build_prompt(prompt, conversation_history=None, message_history=None):
    """
    Builds a prompt for the LLM request using the existing build_context function.
    """
    history = [{"role": "user", "content": prompt}]
    return build_context(history, conversation_history, message_history)

import openai
import os
from dotenv import load_dotenv
from utils.log import log, debug
import json
import traceback

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

def llm_request(history):
    """
    Sends a request to the OpenAI-compatible API using the ChatCompletion endpoint with streaming.
    Processes and prints the response in real time.
    """
    debug("Starting LLM request")
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
        log("Request history: " + str(history))

        debug("Sending request to API")
        # Send the request with streaming enabled
        response = client.chat.completions.create(
            model=model,
            messages=history,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=True
        )
        debug("Got initial streaming response")

        # Process the streaming response
        collected_messages = []
        debug("Starting to process stream")
        for chunk in response:
            debug(f"Received chunk: {chunk}")
            if chunk.choices[0].delta.content is not None:
                content = chunk.choices[0].delta.content
                collected_messages.append(content)
                print(content, end='', flush=True)  # Print in real-time
        
        full_response = ''.join(collected_messages)
        debug(f"Completed response length: {len(full_response)}")
        log(f"Completed response: {full_response[:100]}...")  # Log first 100 chars
        return full_response

    except Exception as e:
        debug(f"Error in llm_request: {str(e)}")
        debug(f"Full traceback: {traceback.format_exc()}")
        log(f"Error in llm_request: {str(e)}")
        log(f"Full traceback: {traceback.format_exc()}")
        return None

def build_context(history, conversation_history, message_history):
    """Build context for the LLM request from various history sources."""
    if conversation_history:
        history.extend(conversation_history)
    if message_history:
        for msg in message_history:
            history.append({"role": "user", "content": msg})
    memories = think.memory.load_memories()
    if memories:
        for mem in memories:
            history.append({"role": "user", "content": mem})
    return history

def build_prompt(prompt, conversation_history=None, message_history=None):
    """
    Builds a prompt for the LLM request using the existing build_context function.
    """
    history = [{"role": "user", "content": prompt}]
    return build_context(history, conversation_history, message_history)
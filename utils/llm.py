import requests
from utils.log import log
import think.memory as memory
import os
from dotenv import load_dotenv
import json

def one_shot_request(prompt, system_context):
    history = []
    history.append({"role": "system", "content": system_context})
    history.append({"role": "user", "content": prompt})
    response = llm_request(history)
    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"]
    else:
        log("Error in one_shot_request")
        return None

import openai
import os
from dotenv import load_dotenv
from utils.log import log
def llm_request(history):
    """
    Sends a request to the OpenAI-compatible API using the ChatCompletion endpoint with streaming.
    Processes and prints the response in real time.
    """
    load_dotenv()
    model = os.getenv("MODEL", "llama3.1:8b-instruct-q8_0")
    temperature = float(os.getenv("TEMPERATURE", 0.7))
    max_tokens = int(os.getenv("MAX_TOKENS", 1024))
    api_url = os.getenv("API_URL")
    truncation_length = os.getenv("TRUNCATION_LENGTH")
    max_new_tokens = os.getenv("MAX_NEW_TOKENS")

    try:
        # Initialize OpenAI-compatible client
        client = openai.OpenAI(
            api_key=os.getenv("OPENAI_API_KEY") or "test",
            base_url=api_url,
        )

        # Send the request with streaming enabled
        response = client.chat.completions.create(
            model=model,
            messages=history,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=True,  # Enable streaming
        )

        # Process and print streamed chunks
        # log("Streaming response:")
        result = ""
        for chunk in response:
            message_content = chunk.choices[0].delta.content or ""
            result += message_content
            print(message_content, end="", flush=True)  # Real-time printing
    
        return result
    except Exception as e:
        log(f"Exception during OpenAI request: {e}")
        raise


def build_context(history, conversation_history, message_history):
    context = ""
    if conversation_history:
        context += "Context:\n"
        for convo in conversation_history:
            if convo:
                context += str(convo)
    if message_history:
        context += "\nMessages:\n"
        for message in message_history:
            if message:
                context += str(message)
    memories = memory.load_memories()
    if memories:
        context += "\nMemories:\n"
        for mem in memories:
            context += mem
    if context:
        history.append(
            {
                "role": "user",
                "content": str(context),
            }
        )
    return history


def build_prompt(base_prompt):
    prompt = []
    prompt.append({"role": "system", "content": base_prompt})

    return prompt

def send(history):
    return llm_request(history)
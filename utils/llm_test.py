import os
import json
from typing import List, Dict, Optional
from utils.log import log, debug
from utils.llm import llm_request

def test_llm_connection() -> bool:
    """Test if the LLM server is accessible.
    
    Returns:
        bool: True if LLM is accessible, False otherwise
    """
    test_prompt = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Respond with 'ok' if you receive this message."}
    ]
    
    try:
        response = llm_request(test_prompt)
        return response is not None and len(response) > 0
    except Exception as e:
        log(f"LLM connection test failed: {str(e)}")
        return False

def mock_llm_request(messages: List[Dict[str, str]]) -> Optional[str]:
    """Mock implementation of llm_request for testing.
    
    Args:
        messages: List of message dictionaries with 'role' and 'content'
        
    Returns:
        str: Mock response based on the last user message
    """
    try:
        # Extract the last user message
        user_messages = [m for m in messages if m["role"] == "user"]
        if not user_messages:
            return "I don't see any user messages to respond to."
        
        last_message = user_messages[-1]["content"].lower()
        
        # Simple pattern matching for mock responses
        if "hello" in last_message or "hi" in last_message:
            return "Hello! I'm a mock LLM response. The real LLM server appears to be unavailable."
        elif "task" in last_message or "todo" in last_message:
            return json.dumps({
                "task": "Example task from mock LLM",
                "priority": 3,
                "description": "This is a mock task response since the LLM server is unavailable",
                "status": "pending"
            })
        elif "search" in last_message or "find" in last_message:
            return "I would search for that, but I'm currently a mock response since the LLM is unavailable."
        else:
            return "I'm a mock LLM response. The real LLM server appears to be unavailable. I can only provide basic responses."
            
    except Exception as e:
        log(f"Error in mock_llm_request: {str(e)}")
        return None

def get_llm_handler():
    """Get the appropriate LLM handler based on server availability.
    
    Returns:
        function: Either the real llm_request or mock_llm_request
    """
    if test_llm_connection():
        log("LLM server is accessible, using real implementation")
        return llm_request
    else:
        log("LLM server is not accessible, using mock implementation")
        return mock_llm_request

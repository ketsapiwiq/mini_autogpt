import os
import json
from typing import List, Dict, Optional
from utils.log import log, debug
from utils.llm import llm_request, test_function_calling_support, llm_request_with_functions
import pytest
from unittest.mock import patch, MagicMock

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

# Ollama Function Calling Tests
def test_ollama_function_calling_support():
    """Test if function calling support detection works correctly."""
    support = test_function_calling_support()
    # This test is informational - it should pass whether support exists or not
    assert isinstance(support, bool), "Function calling support test should return a boolean"

@pytest.mark.skipif(not test_function_calling_support(), reason="Ollama function calling not supported")
def test_ollama_function_execution():
    """Test actual function execution through Ollama when supported."""
    def add_numbers(a: int, b: int) -> int:
        return a + b

    available_functions = {'add_numbers': add_numbers}
    history = [
        {"role": "user", "content": "What is 2 + 3?"}
    ]

    response = llm_request(history, available_functions=available_functions)
    assert response is not None, "Should get a response from Ollama"

@patch('ollama.chat')
def test_ollama_function_calling_fallback(mock_chat):
    """Test fallback to normal chat when function calling fails."""
    # Mock chat to simulate function calling failure
    mock_response = MagicMock()
    mock_response.message.content = "Regular chat response"
    mock_response.message.tool_calls = None
    mock_chat.return_value = mock_response

    def test_func(x: int) -> int:
        return x * 2

    history = [{"role": "user", "content": "Double the number 5"}]
    available_functions = {'test_func': test_func}

    response = llm_request(history, available_functions=available_functions)
    assert response is not None, "Should get a fallback response"
    assert isinstance(response, str), "Response should be a string"

@patch('ollama.chat')
def test_ollama_function_calling_success(mock_chat):
    """Test successful function calling through Ollama."""
    # Mock successful function call
    mock_response = MagicMock()
    mock_response.message.tool_calls = [
        MagicMock(
            function=MagicMock(
                name='test_func',
                arguments={'x': 5}
            )
        )
    ]
    mock_chat.return_value = mock_response

    def test_func(x: int) -> int:
        return x * 2

    history = [{"role": "user", "content": "Double the number 5"}]
    available_functions = {'test_func': test_func}

    with patch('utils.llm.test_function_calling_support', return_value=True):
        response = llm_request(history, available_functions=available_functions)
        assert response is not None, "Should get a response"

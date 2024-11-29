"""Basic tests for mini_autogpt."""
import pytest
from utils.error_handling import ErrorCounter
from utils.log import log
import json

def test_error_counter():
    """Test the ErrorCounter singleton."""
    counter = ErrorCounter()
    counter.reset()
    
    assert counter.get_count() == 0
    counter.increment()
    assert counter.get_count() == 1
    assert not counter.should_exit()
    
    # Reset and test max failures
    counter.reset()
    for _ in range(ErrorCounter.MAX_FAILURES + 1):
        counter.increment()
    assert counter.should_exit()

def test_json_validation():
    """Test JSON validation functions."""
    from action.action_decisions import validate_json
    
    # Test valid command JSON
    valid_json = {
        "command": {
            "name": "test_command",
            "args": {}
        }
    }
    assert validate_json(valid_json)
    
    # Test invalid JSONs
    assert not validate_json(None)
    assert not validate_json("")
    assert not validate_json({})
    assert not validate_json({"command": "not_dict"})
    assert not validate_json({"command": {"no_name": True, "args": {}}})
    assert not validate_json({"command": {"name": "test", "no_args": True}})

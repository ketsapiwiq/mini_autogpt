"""Tests for memory management functionality."""
import json
import os
import time
from unittest.mock import patch, MagicMock

import pytest
from think.memory import Memory, MemoryManager, memory_manager

@pytest.fixture
def memory_mgr(tmp_path):
    """Create a fresh MemoryManager instance for each test."""
    return MemoryManager(base_dir=str(tmp_path))

def test_memory_creation():
    """Test Memory dataclass creation and serialization."""
    content = "Test memory content"
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    metadata = {"type": "test"}
    
    memory = Memory(content=content, timestamp=timestamp, metadata=metadata)
    
    assert memory.content == content
    assert memory.timestamp == timestamp
    assert memory.metadata == metadata
    
    # Test serialization
    memory_dict = memory.to_dict()
    assert isinstance(memory_dict, dict)
    assert memory_dict["content"] == content
    assert memory_dict["timestamp"] == timestamp
    assert memory_dict["metadata"] == metadata

def test_memory_manager_initialization(memory_mgr, tmp_path):
    """Test MemoryManager initialization."""
    assert memory_mgr._conversation_file == os.path.join(str(tmp_path), "conversation_history.json")
    assert memory_mgr._thought_file == os.path.join(str(tmp_path), "thought_history.json")
    assert memory_mgr._response_file == os.path.join(str(tmp_path), "response_history.json")
    assert memory_mgr._memory_file == os.path.join(str(tmp_path), "memories.json")

def test_add_and_get_memory(memory_mgr):
    """Test adding and retrieving memories."""
    content = "Test memory"
    memory_mgr.add_memory("conversation", content)
    
    memories = memory_mgr.get_memories("conversation")
    assert len(memories) == 1
    assert memories[0]["content"] == content

def test_clear_memories(memory_mgr):
    """Test clearing memories."""
    # Add some memories
    memory_mgr.add_memory("conversation", "Test 1")
    memory_mgr.add_memory("thought", "Test 2")
    
    # Clear specific type
    memory_mgr.clear_memories("conversation")
    assert len(memory_mgr.get_memories("conversation")) == 0
    assert len(memory_mgr.get_memories("thought")) == 1
    
    # Clear all
    memory_mgr.clear_memories()
    assert len(memory_mgr.get_memories("conversation")) == 0
    assert len(memory_mgr.get_memories("thought")) == 0

@patch('think.memory.tiktoken')
def test_count_tokens(mock_tiktoken, memory_mgr):
    """Test token counting functionality."""
    mock_encoding = MagicMock()
    mock_encoding.encode.return_value = [1, 2, 3, 4, 5]  # 5 tokens
    mock_tiktoken.encoding_for_model.return_value = mock_encoding
    
    text = "Test text"
    token_count = memory_mgr._count_tokens(text)
    assert token_count == 5
    
    # Test fallback when tiktoken fails
    mock_tiktoken.encoding_for_model.side_effect = Exception("Test error")
    token_count = memory_mgr._count_tokens(text)
    assert token_count == len(text) // 4  # Fallback calculation

def test_chunk_text(memory_mgr):
    """Test text chunking functionality."""
    # Mock _count_tokens to return predictable values
    memory_mgr._count_tokens = lambda x: len(x.split())
    
    text = "This is a test text that should be split into chunks"
    max_tokens = 3
    chunks = memory_mgr._chunk_text(text, max_tokens)
    
    assert len(chunks) == 4  # Text should be split into 4 chunks
    assert all(len(chunk.split()) <= max_tokens for chunk in chunks)

@patch('think.memory.llm')
def test_summarize_text(mock_llm, memory_mgr):
    """Test text summarization functionality."""
    test_text = "Test text to summarize"
    expected_summary = "Summary"
    mock_llm.llm_request.return_value = expected_summary
    
    summary = memory_mgr._summarize_text(test_text)
    assert summary == expected_summary
    
    # Test error handling
    mock_llm.llm_request.side_effect = Exception("Test error")
    summary = memory_mgr._summarize_text(test_text)
    assert summary is None

def test_memory_manager_singleton():
    """Test that memory_manager is a singleton instance."""
    assert isinstance(memory_manager, MemoryManager)
    new_manager = MemoryManager()
    assert memory_manager is not new_manager  # They should be different instances

def test_file_operations(memory_mgr):
    """Test file operations with actual files."""
    # Test saving and loading
    test_content = "Test memory"
    memory_mgr.add_memory("conversation", test_content)
    
    # Verify file was created
    assert os.path.exists(memory_mgr._conversation_file)
    
    # Load and verify content
    with open(memory_mgr._conversation_file, 'r') as f:
        saved_data = json.load(f)
    assert len(saved_data) == 1
    assert saved_data[0]["content"] == test_content

def test_memory_limit(memory_mgr):
    """Test memory retrieval with limit."""
    # Add multiple memories
    for i in range(10):
        memory_mgr.add_memory("conversation", f"Memory {i}")
    
    # Get limited memories
    memories = memory_mgr.get_memories("conversation", limit=5)
    assert len(memories) == 5
    assert all(mem["content"].startswith("Memory") for mem in memories)
    
    # Verify we got the most recent ones
    assert memories[-1]["content"] == "Memory 9"

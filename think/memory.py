import json
import os
import traceback
import time
from dataclasses import dataclass, asdict
from typing import Optional, List, Dict, Any

import tiktoken
import think.prompt as prompt
import utils.llm as llm
from utils.log import log

@dataclass
class Memory:
    """Base class for all memory types."""
    content: str
    timestamp: str
    metadata: Dict[str, Any] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert memory to dictionary."""
        return asdict(self)

class MemoryManager:
    """Manages different types of memory storage and retrieval."""
    
    def __init__(self, base_dir: str = None):
        self.base_dir = base_dir or os.getcwd()
        self._conversation_file = os.path.join(self.base_dir, "conversation_history.json")
        self._thought_file = os.path.join(self.base_dir, "thought_history.json")
        self._response_file = os.path.join(self.base_dir, "response_history.json")
        self._memory_file = os.path.join(self.base_dir, "memories.json")
        
    def _load_json(self, filename: str) -> List[Dict]:
        """Load data from a JSON file."""
        try:
            if os.path.exists(filename):
                with open(filename, "r") as f:
                    return json.load(f)
            return []
        except Exception as e:
            log(f"Error loading {filename}: {e}")
            return []
            
    def _save_json(self, filename: str, data: List[Dict]) -> None:
        """Save data to a JSON file."""
        try:
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            with open(filename, "w") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            log(f"Error saving to {filename}: {e}")
            
    def add_memory(self, memory_type: str, content: str, metadata: Dict = None) -> None:
        """Add a new memory of specified type."""
        memory = Memory(
            content=content,
            timestamp=time.strftime("%Y-%m-%d %H:%M:%S"),
            metadata=metadata or {}
        )
        
        filename = getattr(self, f"_{memory_type}_file")
        memories = self._load_json(filename)
        memories.append(memory.to_dict())
        self._save_json(filename, memories)
        
    def get_memories(self, memory_type: str, limit: int = None) -> List[Dict]:
        """Get memories of specified type."""
        filename = getattr(self, f"_{memory_type}_file")
        memories = self._load_json(filename)
        return memories[-limit:] if limit else memories
        
    def clear_memories(self, memory_type: str = None) -> None:
        """Clear memories of specified type or all if type is None."""
        if memory_type:
            filename = getattr(self, f"_{memory_type}_file")
            self._save_json(filename, [])
        else:
            for attr in dir(self):
                if attr.endswith('_file'):
                    self._save_json(getattr(self, attr), [])
                    
    def summarize_memories(self, memory_type: str, max_tokens: int = 3000) -> str:
        """Summarize memories of specified type."""
        memories = self.get_memories(memory_type)
        if not memories:
            return ""
            
        # Combine memories into chunks
        text = "\n".join(m["content"] for m in memories)
        chunks = self._chunk_text(text, max_tokens)
        
        # Summarize each chunk
        summaries = []
        for chunk in chunks:
            summary = self._summarize_text(chunk)
            if summary:
                summaries.append(summary)
                
        return "\n".join(summaries)
        
    def _chunk_text(self, text: str, max_tokens: int = 3000) -> List[str]:
        """Split text into chunks based on token count."""
        if not text:
            return []
            
        words = text.split()
        if not words:
            return []
            
        chunks = []
        current_chunk = []
        current_length = 0
        
        for word in words:
            word_tokens = self._count_tokens(word)
            if current_length + word_tokens > max_tokens and current_chunk:
                chunks.append(" ".join(current_chunk))
                current_chunk = [word]
                current_length = word_tokens
            else:
                current_chunk.append(word)
                current_length += word_tokens
                
        if current_chunk:
            chunks.append(" ".join(current_chunk))
            
        return chunks
        
    def _count_tokens(self, text: str) -> int:
        """Count tokens in text using tiktoken."""
        try:
            encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
            return len(encoding.encode(text))
        except Exception as e:
            log(f"Error counting tokens: {e}")
            return len(text) // 4  # Rough estimate
            
    def _summarize_text(self, text: str, max_new_tokens: int = 100) -> Optional[str]:
        """Summarize text using LLM."""
        try:
            history = [
                {"role": "system", "content": prompt.summarize_conversation},
                {"role": "user", "content": f"Please summarize: {text}"}
            ]
            return llm.llm_request(history)
        except Exception as e:
            log(f"Error summarizing text: {e}")
            return None

# Global instance
memory_manager = MemoryManager()

def log(message):
    # print with purple color
    print("\033[94m" + str(message) + "\033[0m")

def load_dotenv():
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except Exception as e:
        log(f"Error loading .env file: {e}")

def load_conversation_history():
    """Load the conversation history from a file."""
    try:
        conversation_history = memory_manager.get_memories("conversation")
        return conversation_history
    except Exception as e:
        log(f"Error loading conversation history: {e}")
        return []

def save_conversation_history(conversation_history):
    """Save the conversation history to a file."""
    try:
        memory_manager.clear_memories("conversation")
        for message in conversation_history:
            memory_manager.add_memory("conversation", message)
    except Exception as e:
        log(f"Error saving conversation history: {e}")

def add_to_conversation_history(message):
    """Add a message to the conversation history and save it."""
    try:
        memory_manager.add_memory("conversation", message)
    except Exception as e:
        log(f"Error adding to conversation history: {e}")

def forget_conversation_history():
    """Forget the conversation history."""
    try:
        memory_manager.clear_memories("conversation")
    except Exception as e:
        log(f"Error forgetting conversation history: {e}")

def load_thought_history():
    """Load the thought history from a file."""
    try:
        thought_history = memory_manager.get_memories("thought")
        return thought_history
    except Exception as e:
        log(f"Error loading thought history: {e}")
        return []

def save_thought_history(thought_history):
    """Save the thought history to a file."""
    try:
        memory_manager.clear_memories("thought")
        for thought in thought_history:
            memory_manager.add_memory("thought", thought)
    except Exception as e:
        log(f"Error saving thought history: {e}")

def add_to_thought_history(thought):
    """Add a thought to the thought history and save it."""
    try:
        memory_manager.add_memory("thought", thought)
    except Exception as e:
        log(f"Error adding to thought history: {e}")

def forget_thought_history():
    """Forget the thought history."""
    try:
        memory_manager.clear_memories("thought")
    except Exception as e:
        log(f"Error forgetting thought history: {e}")

def load_response_history():
    """Load the response history from a file."""
    try:
        response_history = memory_manager.get_memories("response")
        return response_history
    except Exception as e:
        log(f"Error loading response history: {e}")
        return []

def save_response_history(response_history):
    """Save the response history to a file."""
    try:
        memory_manager.clear_memories("response")
        for response in response_history:
            memory_manager.add_memory("response", response)
    except Exception as e:
        log(f"Error saving response history: {e}")

def add_to_response_history(question, response):
    """Add a question and its corresponding response to the history."""
    try:
        memory_manager.add_memory("response", f"{question}\n{response}")
    except Exception as e:
        log(f"Error adding to response history: {e}")

def forget_response_history():
    """Forget the response history."""
    try:
        memory_manager.clear_memories("response")
    except Exception as e:
        log(f"Error forgetting response history: {e}")

def load_memories():
    """Load the memories from a file."""
    try:
        memories = memory_manager.get_memories("memory")
        return memories
    except Exception as e:
        log(f"Error loading memories: {e}")
        return []

def save_memories(memories):
    """Save the memories to a file."""
    try:
        memory_manager.clear_memories("memory")
        for memory in memories:
            memory_manager.add_memory("memory", memory)
    except Exception as e:
        log(f"Error saving memories: {e}")

def add_to_memories(memory):
    """Add a memory to the memories and save it."""
    try:
        memory_manager.add_memory("memory", memory)
    except Exception as e:
        log(f"Error adding to memories: {e}")

def forget_memories():
    """Forget the memories."""
    try:
        memory_manager.clear_memories("memory")
    except Exception as e:
        log(f"Error forgetting memories: {e}")

def get_previous_message_history(conversation_history):
    """Get the previous message history with improved context handling."""
    try:
        if not conversation_history:
            return "There is no previous message history."

        # Get last few messages for immediate context
        recent_messages = conversation_history[-10:]
        
        # Summarize older messages if they exist
        older_messages = conversation_history[:-10] if len(conversation_history) > 10 else []
        if older_messages:
            tokens = memory_manager._count_tokens(str(older_messages))
            if tokens > 1000:
                chunks = memory_manager._chunk_text(str(older_messages))
                summaries = []
                for chunk in chunks:
                    summary = memory_manager._summarize_text(chunk)
                    if summary:
                        summaries.append(summary)
                context = "Previous conversation summary: " + " ".join(summaries)
            else:
                context = "Previous messages: " + str(older_messages)
                
            return context + "\nRecent messages: " + str(recent_messages)
        
        return str(recent_messages)
    except Exception as e:
        log(f"Error while getting previous message history: {e}")
        log(traceback.format_exc())
        return "Error retrieving message history"

def get_response_history():
    """Retrieve the history of responses."""
    try:
        response_history = load_response_history()
        if len(response_history) == 0:
            return "There is no previous response history."

        # Assuming a similar function exists for counting tokens and summarizing
        tokens = memory_manager._count_tokens(str(response_history))
        if tokens > 500:
            log("Response history is over 500 tokens. Summarizing...")
            chunks = memory_manager._chunk_text(str(response_history))
            summaries = []
            for chunk in chunks:
                summary = memory_manager._summarize_text(chunk)
                if summary:
                    summaries.append(summary)
            summarized_history = " ".join(summaries)
            # summarized_history += " " + " ".join(response_history[-6:])
            return summarized_history

        return response_history
    except Exception as e:
        log(f"Error while getting previous response history: {e}")
        log(traceback.format_exc())
        exit(1)

def get_previous_thought_history(thought_history):
    """Get the previous message history."""
    try:
        if len(thought_history) == 0:
            return "There is no previous message history."

        tokens = memory_manager._count_tokens(str(thought_history))
        if tokens > 200:
            log("Message history is over 3000 tokens. Summarizing...")
            chunks = memory_manager._chunk_text(str(thought_history))
            summaries = []
            for chunk in chunks:
                summary = memory_manager._summarize_text(chunk)
                if summary:
                    summaries.append(summary)
            summarized_history = " ".join(summaries)
            summarized_history += " " + " ".join(thought_history[-6:])
            return summarized_history

        return thought_history
    except Exception as e:
        log(f"Error while getting previous message history: {e}")
        log(traceback.format_exc())
        exit(1)

def forget_everything():
    """Forget everything."""
    print("Forgetting everything...")
    
    memory_manager.clear_memories()
    print("My memory is empty now, I am ready to learn new things! \n")

load_dotenv()

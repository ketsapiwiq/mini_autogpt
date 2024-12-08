from utils.llm_test import get_llm_handler
from utils.log import log

def main():
    # Get the appropriate LLM handler (real or mock)
    llm_handler = get_llm_handler()
    
    # Test some example prompts
    test_prompts = [
        [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Hello! Are you working?"}
        ],
        [
            {"role": "system", "content": "You are a task analyzer."},
            {"role": "user", "content": "Create a task to test the system"}
        ],
        [
            {"role": "system", "content": "You are a search assistant."},
            {"role": "user", "content": "Search for information about LLMs"}
        ]
    ]
    
    # Try each prompt
    for prompt in test_prompts:
        log("\nTesting prompt:", prompt[-1]["content"])
        response = llm_handler(prompt)
        log("Response:", response)
        log("-" * 50)

if __name__ == "__main__":
    main()

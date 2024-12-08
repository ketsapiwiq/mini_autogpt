import os
import json
import autogen
from autogen import AssistantAgent, UserProxyAgent
from autogen.agentchat.contrib.reasoning_agent import ReasoningAgent, visualize_tree
from utils.task_tree import get_highest_priority_task, update_task_results

# Configure the model
llm_config = {"model": "llama3.1:8b-instruct-q8_0", "api_key":"sdfsdf", "base_url": "http://192.168.1.50:11434/v1"}

# Import task-related modules
from action.tasks import ACTIVE_TASKS_DIR, COMPLETED_TASKS_DIR

def process_current_task():
    """Process the highest priority pending task"""
    # Get the current highest priority task
    current_task = get_highest_priority_task()
    
    if not current_task:
        print("No pending tasks found.")
        return None
    
    print(f"Processing task: {current_task.get('title', 'Untitled Task')}")
    
    # Prepare task processing
    assistant = autogen.AssistantAgent(
        "task-assistant",
        llm_config=llm_config,
        is_termination_msg=lambda x: x.get("content", "").find("TERMINATE") >= 0,
    )

    code_interpreter = autogen.UserProxyAgent(
        "task-code-interpreter",
        human_input_mode="NEVER",
        code_execution_config={
            "work_dir": "coding",
            "use_docker": False,
        },
        max_consecutive_auto_reply=5,
        default_auto_reply="",
        is_termination_msg=lambda x: x.get("content", "").find("TERMINATE") >= 0,
    )

    # Create Society of Mind Agent for task processing
    society_of_mind_agent = SocietyOfMindAgent(
        "task_society_of_mind",
        chat_manager=autogen.GroupChatManager(
            groupchat=autogen.GroupChat(
                agents=[assistant, code_interpreter],
                messages=[],
                max_round=8
            ),
            llm_config=llm_config
        ),
        llm_config=llm_config,
    )

    # Initiate chat with the task description
    result = society_of_mind_agent.initiate_chat(
        code_interpreter, 
        message=f"Process this task: {current_task.get('description', 'No description')}"
    )

    # Update task results
    update_result = update_task_results(current_task, result)
    
    # Move task to completed if successful
    if update_result.get('success', False):
        current_task['status'] = 'completed'
        
        # Move task file to completed directory
        old_path = os.path.join(ACTIVE_TASKS_DIR, f"{current_task['id']}.json")
        new_path = os.path.join(COMPLETED_TASKS_DIR, f"{current_task['id']}.json")
        
        with open(new_path, 'w') as f:
            json.dump(current_task, f, indent=2)
        
        os.remove(old_path)
        
        print(f"Task {current_task['id']} completed successfully.")
    
    return update_result

# Main execution
if __name__ == "__main__":
    from autogen.agentchat.contrib.society_of_mind_agent import SocietyOfMindAgent
    
    # Process the current task
    result = process_current_task()
    
    # Optional: Save result to file
    if result:
        with open('societyofminds_result.txt', 'w') as f:
            json.dump(result, f, indent=2)
    
    print("Task processing complete.")

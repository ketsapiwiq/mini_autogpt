import json
import think.memory as memory
import think.prompt as prompt
from utils.task_tree import create_task_from_json
import utils.llm as llm
from action.action_decisions import decide, validate_json, extract_json_from_response
from action.action_execute import take_action
from utils.log import log, save_debug
from utils.task_manager import get_first_task, update_task_results
from utils.error_handling import ErrorCounter
import datetime
import traceback

def process_thoughts():
    thinking = generate_thoughts()  # takes
    print("THOUGHTS : " + thinking)
    decision = decide(thinking)
    print("DECISIONS : " + str(decision))
    evaluated_decision = analyze_decision(thinking, decision)
    print("EVALUATED DECISION : " + str(evaluated_decision))
    take_action(evaluated_decision)


def analyze_decision(thoughts, decision):
    # combine thoughts and decision and ask llm to evaluate the decision json and output an improved one
    history = llm.build_prompt(prompt.get_evaluation_prompt())
    
    # If decision is to ask user, include conversation history for context
    try:
        # Handle the decision input
        if isinstance(decision, str):
            try:
                decision_dict = json.loads(decision)
            except json.JSONDecodeError:
                decision_dict = decision
        else:
            decision_dict = decision

        if isinstance(decision_dict, dict) and decision_dict.get("command") == "ask_user":
            history = llm.build_context(
                history=history,
                conversation_history=memory.get_response_history(),
                message_history=memory.load_response_history()[-2:]
            )
    except (json.JSONDecodeError, AttributeError):
        pass
        
    context = f"Thoughts: {thoughts} \n Decision: {decision}"
    history.append({"role": "user", "content": context})
    response = llm.llm_request(history)

    # Handle the response
    if isinstance(response, dict):
        return response

    try:
        if not validate_json(response):
            response = extract_json_from_response(response)
        
        if validate_json(response):
            if isinstance(response, dict):
                return response
            return json.loads(response)
        else:
            ErrorCounter.increment()
            if ErrorCounter.get_count() >= 5:
                log("Got too many bad quality responses!")
                exit(1)
            return None
    except Exception as e:
        log(f"Error processing response: {str(e)}")
        ErrorCounter.increment()
        return None


def generate_thoughts():
    """
    Performs the thinking process and returns the thoughts generated by the assistant.
    First checks for any pending tasks and thinks about those before general thinking.

    Returns:
        str: The thoughts generated by the assistant.

    Raises:
        Exception: If there is an error in the thinking process.
    """
    
    log("*** I am thinking... ***")
    
    # Get the highest priority task first
    current_task = get_first_task()
    
    history = llm.build_prompt(prompt.get_thought_prompt())
    thought_history = memory.load_thought_history()
    
    # Process thought history more carefully
    thought_summaries = []
    for item in thought_history:
        try:
            if isinstance(item, str):
                thought_data = json.loads(item)
            else:
                thought_data = item
            if isinstance(thought_data, dict) and "summary" in thought_data:
                thought_summaries.append(thought_data["summary"])
        except (json.JSONDecodeError, AttributeError):
            continue
    
    # Get latest user message and create task if needed
    message_history = memory.load_response_history()[-5:]  # Get last 5 messages for better context
    if message_history:
        latest_messages = [msg for msg in message_history if msg.get("role") == "user"]
        if latest_messages:
            user_message = latest_messages[-1].get("content")
            # Create task from user message
            task_history = llm.build_prompt("""You are a task analyzer. Extract a clear task from the user message.
Output in this JSON format (priority 1-5, lower is higher priority):
{
    "task": "clear task description",
    "priority": priority_number,
    "description": "detailed description of what needs to be done",
    "status": "pending"
}
If no clear task can be extracted, return null.""")
            task_history.append({"role": "user", "content": f"Extract task from this message:\n{user_message}"})
            
            try:
                task_response = llm.llm_request(task_history)
                task_data = json.loads(task_response) if validate_json(task_response) else None
                if task_data:
                    # Create task with proper parameter names
                    create_task_from_json(task_data)
                    log(f"Successfully created task: {task_data['task']}")
            except json.JSONDecodeError as e:
                log(f"Error parsing task JSON response: {e}")
                log(f"Raw response: {task_response}")
            except KeyError as e:
                log(f"Missing required task field: {e}")
                log(f"Task data: {task_data}")
            except Exception as e:
                log(f"Unexpected error creating task: {e}")
                log(traceback.format_exc())
    
    # Build context with improved history handling
    history = llm.build_context(
        history=history,
        conversation_history=thought_summaries[-5:] if thought_summaries else None,  # Last 5 thought summaries
        message_history=message_history
    )

    # If there's a task, think about it specifically
    if current_task and 'task' in current_task:
        log(f"*** Thinking about task: {current_task['task']} ***")
        
        # Add task context
        task_context = {
            "current_task": current_task,
            "thought_history": thought_summaries[-3:] if thought_summaries else [],  # Last 3 related thoughts
            "message_context": message_history[-3:] if message_history else []  # Last 3 messages
        }
        
        history.append(
            {
                "role": "user",
                "content": f"Current task and context:\n{json.dumps(task_context, indent=2)}\n\nAnalyze the task and context, then formulate detailed thoughts about how to proceed.",
            },
        )
    else:
        # Default general thinking if no specific task
        history.append(
            {
                "role": "user",
                "content": "Based on the current context, formulate your thoughts about what should be done next.",
            },
        )
    
    try:
        response = llm.llm_request(history)
        thoughts = response
        log("*** I think I have finished thinking! *** \n")
        
        # Save thought with metadata
        thought_data = {
            "timestamp": datetime.datetime.utcnow().isoformat(),
            "thought": thoughts,
            "summary": thoughts[:200] + "..." if len(thoughts) > 200 else thoughts,
            "context": {
                "task_id": current_task.get("id") if current_task else None,
                "message_count": len(message_history) if message_history else 0
            }
        }
        # memory.save_thought(json.dumps(thought_data), context=history)
        
        # If we were thinking about a specific task, update its results
        if current_task:
            # Extract interesting insights using another LLM call
            insight_history = llm.build_prompt("""You are a task analyzer. Extract the most interesting and actionable insights from the thinking results.
Focus on concrete conclusions and next steps. Be concise and clear. Output in this format:
{
    "key_insights": ["insight 1", "insight 2", ...],
    "next_steps": ["step 1", "step 2", ...],
    "status_update": "brief status update"
}""")
            insight_history.append({"role": "user", "content": f"Extract insights from these thoughts:\n{thoughts}"})
            
            try:
                insight_response = llm.llm_request(insight_history)
                # Extract the JSON part from the response
                insights = extract_json_from_response(insight_response)
                if validate_json(insights):
                    update_task_results(current_task, insights)
            except Exception as e:
                log(f"Error extracting insights: {e}")
        
        return thoughts
    except Exception as e:
        log(f"Error in thinking process: {e}")
        log(traceback.format_exc())
        raise e

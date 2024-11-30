"""User interaction commands."""
from typing import Dict, Any, Optional
from . import Command
from .prompt_builder import BasicPromptTemplate
from utils.simple_telegram import TelegramUtils
from utils.log import log
import os
import json

telegram = TelegramUtils.get_instance(
    api_key=os.getenv('TELEGRAM_API_KEY'),
    chat_id=os.getenv('TELEGRAM_CHAT_ID')
)

class SendMessageCommand(Command):
    """Command to send a message to the user via Telegram."""
    
    def validate_args(self, args: Dict[str, Any]) -> bool:
        return isinstance(args.get("message"), str)
    
    def get_args(self) -> Dict[str, str]:
        return {
            "message": "The message to send to the user. Should be clear and concise."
        }
    
    def get_prompt_template(self) -> Optional[BasicPromptTemplate]:
        """Get prompt template for message formatting."""
        template = """You are crafting a message to send to the user. Follow these guidelines:

1. Purpose: {purpose}
2. Context: {context}

Guidelines for message composition:
- Be clear and concise
- Use appropriate tone and formality
- Include all necessary information
- Avoid ambiguity
- Format for readability

Your task is to format this message:
{message}

Consider:
1. Is the message clear and unambiguous?
2. Does it convey all necessary information?
3. Is the tone appropriate for the context?
4. Is it properly formatted for readability?"""
        return BasicPromptTemplate(template)
    
    def execute(self, args: Dict[str, Any]) -> Dict[str, Any]:
        message = args["message"]
        log(f"Sending message: {message}")
        telegram.send_message(message)
        return {"status": "success"}

class AskUserCommand(Command):
    """Command to ask the user a question and wait for their response via Telegram."""
    
    def validate_args(self, args: Dict[str, Any]) -> bool:
        return isinstance(args.get("message"), str)
    
    def get_args(self) -> Dict[str, str]:
        return {
            "message": "The question or prompt to send to the user. Should be clear and specific."
        }
    
    def get_prompt_template(self) -> Optional[BasicPromptTemplate]:
        """Get prompt template for question formatting."""
        template = """You are formulating a question to ask the user. Follow these guidelines:

Context: {context}
Purpose: {purpose}

Guidelines for question formulation:
- Be specific and focused
- Use clear, unambiguous language
- Provide necessary context
- Make it easy to understand and answer
- Consider the expected response format

Your question:
{message}

Consider:
1. Is the question clear and specific?
2. Have you provided necessary context?
3. Is the expected response format clear?
4. Will the answer provide the information you need?
5. Is follow-up clarification likely to be needed?"""
        return BasicPromptTemplate(template)
    
    def execute(self, args: Dict[str, Any]) -> Dict[str, Any]:
        message = args["message"]
        log(f"Asking user: {message}")
        response = telegram.ask_user(message)
        return {"status": "success", "response": response}

class TellUserCommand(Command):
    """Command to tell something to the user without interaction."""
    
    def validate_args(self, args: Dict[str, Any]) -> bool:
        return isinstance(args.get("message"), str)
    
    def get_args(self) -> Dict[str, str]:
        return {
            "message": "The message to tell the user. Should be clear and informative."
        }
    
    def get_prompt_template(self) -> Optional[BasicPromptTemplate]:
        """Get prompt template for informational message formatting."""
        template = """You are preparing an informational message for the user. Follow these guidelines:

Information Type: {info_type}
Priority Level: {priority}
Context: {context}

Guidelines for informational messages:
- Present information clearly and logically
- Highlight important points
- Use appropriate formatting for readability
- Include relevant context
- Be objective and accurate

Your message:
{message}

Consider:
1. Is the information presented clearly?
2. Are important points highlighted?
3. Is the formatting appropriate?
4. Is necessary context included?
5. Is the tone appropriate for an informational message?"""
        return BasicPromptTemplate(template)
    
    def execute(self, args: Dict[str, Any]) -> Dict[str, Any]:
        message = args["message"]
        log(f"Telling user: {message}")
        telegram.tell_user(message)
        return {"status": "success"}

class ExtractTasksCommand(Command):
    """Extract possible tasks from conversation history."""
    
    def validate_args(self, args: Dict[str, Any]) -> bool:
        """Validate command arguments.
        
        Args:
            args: Dictionary of command arguments
            
        Returns:
            True since this command takes no arguments
        """
        return True

    def get_args(self) -> Dict[str, Dict[str, Any]]:
        """Get command argument descriptions.
        
        Returns:
            Empty dictionary since this command takes no arguments
        """
        return {}

    def execute(self, args: Dict[str, Any]) -> Dict[str, Any]:
        from think.memory import load_response_history
        import utils.llm as llm
        from utils.task_tree import create_task_from_json
        
        # Get conversation history
        message_history = load_response_history()
        
        # Build prompt for task extraction
        task_history = llm.build_prompt("""You are a task analyzer. Extract clear tasks from the conversation history.
Output in this JSON format (priority 1-5, lower is higher priority):
{
    "tasks": [
        {
            "task": "clear task description",
            "priority": priority_number,
            "description": "detailed description of what needs to be done",
            "status": "pending"
        }
    ]
}
If no clear tasks can be extracted, return {"tasks": []}.""")
        
        task_history.append({
            "role": "user", 
            "content": f"Extract tasks from this conversation history:\n{str(message_history)}"
        })
        
        try:
            task_response = llm.llm_request(task_history)
            task_data = json.loads(task_response)
            
            created_tasks = []
            for task in task_data.get("tasks", []):
                task_id = create_task_from_json(task)
                created_tasks.append({
                    "id": task_id,
                    "task": task["task"]
                })
            
            return {
                "status": "success",
                "tasks_created": created_tasks
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
# Register commands
from .registry import CommandRegistry
CommandRegistry.register("send_message", SendMessageCommand)
# ask_user intentionally disabled
# CommandRegistry.register("ask_user", AskUserCommand)
CommandRegistry.register("tell_user", TellUserCommand)
CommandRegistry.register("extract_tasks", ExtractTasksCommand)
CommandRegistry.register("show_conv_history", ExtractTasksCommand)  # Alias for conversation history
# CommandRegistry.register("agent_execute", AgentCommandExecutor)

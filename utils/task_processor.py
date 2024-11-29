import json
import uuid
from datetime import datetime
from typing import Dict, List, Optional

class TaskProcessor:
    def __init__(self, tasks_dir: str = "tasks"):
        self.tasks_dir = tasks_dir
        
    def extract_task_from_message(self, message: str) -> Optional[Dict]:
        """Analyze user message and extract potential tasks"""
        # TODO: Implement task extraction logic using LLM
        if not message:
            return None
            
        task = {
            "id": str(uuid.uuid4()),
            "priority": 3,  # Default priority
            "task": message,
            "status": "pending",
            "created_at": datetime.utcnow().isoformat(),
            "context": {
                "user_message": message,
                "key_insights": []
            }
        }
        return task
        
    def add_task(self, task: Dict) -> str:
        """Add a new task to the system"""
        task_id = task.get("id", str(uuid.uuid4()))
        task_file = f"{self.tasks_dir}/{task_id}.json"
        
        with open(task_file, "w") as f:
            json.dump(task, f, indent=4)
        
        return task_id
        
    def update_task_status(self, task_id: str, status: str, insights: List[str] = None):
        """Update task status and add any new insights"""
        task_file = f"{self.tasks_dir}/{task_id}.json"
        
        with open(task_file, "r") as f:
            task = json.load(f)
            
        task["status"] = status
        task["updated_at"] = datetime.utcnow().isoformat()
        
        if insights:
            task["context"]["key_insights"].extend(insights)
            
        with open(task_file, "w") as f:
            json.dump(task, f, indent=4)
            
    def get_next_task(self) -> Optional[Dict]:
        """Get the highest priority pending task"""
        # TODO: Implement proper task prioritization
        return None  # Placeholder

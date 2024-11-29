import os
import json
import shutil
import unittest
from utils.task_tree import (
    ensure_task_directories,
    create_task,
    get_task,
    update_task_status,
    add_thought,
    get_highest_priority_task,
    create_subtask,
    TASKS_DIR,
    ACTIVE_TASKS_DIR,
    COMPLETED_TASKS_DIR
)

class TestTaskTree(unittest.TestCase):
    def setUp(self):
        """Clean up task directories before each test"""
        if os.path.exists(TASKS_DIR):
            shutil.rmtree(TASKS_DIR)
    
    def tearDown(self):
        """Clean up task directories after each test"""
        if os.path.exists(TASKS_DIR):
            shutil.rmtree(TASKS_DIR)

    def test_ensure_task_directories(self):
        """Test creation of task directory structure"""
        ensure_task_directories()
        self.assertTrue(os.path.exists(TASKS_DIR))
        self.assertTrue(os.path.exists(ACTIVE_TASKS_DIR))
        self.assertTrue(os.path.exists(COMPLETED_TASKS_DIR))

    def test_create_task(self):
        """Test task creation"""
        ensure_task_directories()
        
        task_id = create_task(
            title="Test task",
            description="Test description",
            priority=2,
            source="test"
        )
        
        # Verify task file exists
        task_dir = os.path.join(ACTIVE_TASKS_DIR, task_id)
        task_file = os.path.join(task_dir, "task.json")
        self.assertTrue(os.path.exists(task_dir))
        self.assertTrue(os.path.exists(task_file))
        self.assertTrue(os.path.exists(os.path.join(task_dir, "thoughts")))
        self.assertTrue(os.path.exists(os.path.join(task_dir, "subtasks")))
        
        # Verify task content
        with open(task_file) as f:
            task_data = json.load(f)
        self.assertEqual(task_data["id"], task_id)
        self.assertEqual(task_data["title"], "Test task")
        self.assertEqual(task_data["description"], "Test description")
        self.assertEqual(task_data["priority"], 2)
        self.assertEqual(task_data["source"], "test")
        self.assertEqual(task_data["status"], "pending")

    def test_get_task(self):
        """Test retrieving task data"""
        ensure_task_directories()
        task_id = create_task("Test task", "Test description")
        
        task_data = get_task(task_id)
        self.assertEqual(task_data["id"], task_id)
        self.assertEqual(task_data["title"], "Test task")

    def test_update_task_status(self):
        """Test updating task status"""
        ensure_task_directories()
        task_id = create_task("Test task", "Test description")
        
        # Update to in_progress
        update_task_status(task_id, "in_progress")
        task_data = get_task(task_id)
        self.assertEqual(task_data["status"], "in_progress")
        
        # Complete task and verify it moves to completed directory
        update_task_status(task_id, "completed", {"result": "success"})
        task_data = get_task(task_id)
        self.assertEqual(task_data["status"], "completed")
        self.assertEqual(task_data["results"], {"result": "success"})
        self.assertTrue(os.path.exists(os.path.join(COMPLETED_TASKS_DIR, task_id)))
        self.assertFalse(os.path.exists(os.path.join(ACTIVE_TASKS_DIR, task_id)))

    def test_add_thought(self):
        """Test adding thoughts to a task"""
        ensure_task_directories()
        task_id = create_task("Test task", "Test description")
        
        thought = "This is a test thought"
        add_thought(task_id, thought)
        
        # Verify thought file exists and contains correct content
        thought_dir = os.path.join(ACTIVE_TASKS_DIR, task_id, "thoughts")
        thought_files = os.listdir(thought_dir)
        self.assertEqual(len(thought_files), 1)
        
        with open(os.path.join(thought_dir, thought_files[0])) as f:
            saved_thought = f.read()
        self.assertEqual(saved_thought, thought)

    def test_get_highest_priority_task(self):
        """Test retrieving highest priority task"""
        ensure_task_directories()
        
        # Create tasks with different priorities
        task1_id = create_task("Task 1", "Description 1", priority=3)
        task2_id = create_task("Task 2", "Description 2", priority=1)  # Highest priority
        task3_id = create_task("Task 3", "Description 3", priority=2)
        
        # Complete task2 to ensure it's not returned
        update_task_status(task2_id, "completed")
        
        # Get highest priority pending task
        highest_task = get_highest_priority_task()
        self.assertIsNotNone(highest_task)
        self.assertEqual(highest_task["priority"], 2)  # Task3 should be highest priority now
        self.assertEqual(highest_task["title"], "Task 3")

    def test_create_subtask(self):
        """Test creating subtasks"""
        ensure_task_directories()
        
        # Create parent task
        parent_id = create_task("Parent task", "Parent description", priority=2)
        
        # Create subtask
        subtask_id = create_subtask(parent_id, "Subtask", "Subtask description")
        
        # Verify subtask
        subtask_data = get_task(subtask_id)
        self.assertEqual(subtask_data["parent_task"], parent_id)
        self.assertEqual(subtask_data["priority"], 2)  # Should inherit parent priority
        self.assertEqual(subtask_data["title"], "Subtask")

if __name__ == '__main__':
    unittest.main()

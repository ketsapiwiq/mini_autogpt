import os
import json
import shutil
import pytest
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

@pytest.fixture
def clean_task_dirs():
    """Clean up task directories before and after tests"""
    # Clean up before test
    if os.path.exists(TASKS_DIR):
        shutil.rmtree(TASKS_DIR)
    
    # Run the test
    yield
    
    # Clean up after test
    if os.path.exists(TASKS_DIR):
        shutil.rmtree(TASKS_DIR)

def test_ensure_task_directories(clean_task_dirs):
    """Test creation of task directory structure"""
    ensure_task_directories()
    assert os.path.exists(TASKS_DIR)
    assert os.path.exists(ACTIVE_TASKS_DIR)
    assert os.path.exists(COMPLETED_TASKS_DIR)

def test_create_task(clean_task_dirs):
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
    assert os.path.exists(task_dir)
    assert os.path.exists(task_file)
    assert os.path.exists(os.path.join(task_dir, "thoughts"))
    assert os.path.exists(os.path.join(task_dir, "subtasks"))
    
    # Verify task content
    with open(task_file) as f:
        task_data = json.load(f)
    assert task_data["id"] == task_id
    assert task_data["title"] == "Test task"
    assert task_data["description"] == "Test description"
    assert task_data["priority"] == 2
    assert task_data["source"] == "test"
    assert task_data["status"] == "pending"

def test_get_task(clean_task_dirs):
    """Test retrieving task data"""
    ensure_task_directories()
    task_id = create_task("Test task", "Test description")
    
    task_data = get_task(task_id)
    assert task_data["id"] == task_id
    assert task_data["title"] == "Test task"

def test_update_task_status(clean_task_dirs):
    """Test updating task status"""
    ensure_task_directories()
    task_id = create_task("Test task", "Test description")
    
    # Update to in_progress
    update_task_status(task_id, "in_progress")
    task_data = get_task(task_id)
    assert task_data["status"] == "in_progress"
    
    # Complete task and verify it moves to completed directory
    update_task_status(task_id, "completed", {"result": "success"})
    task_data = get_task(task_id)
    assert task_data["status"] == "completed"
    assert task_data["results"] == {"result": "success"}
    assert os.path.exists(os.path.join(COMPLETED_TASKS_DIR, task_id))
    assert not os.path.exists(os.path.join(ACTIVE_TASKS_DIR, task_id))

def test_add_thought(clean_task_dirs):
    """Test adding thoughts to a task"""
    ensure_task_directories()
    task_id = create_task("Test task", "Test description")
    
    thought = "This is a test thought"
    add_thought(task_id, thought)
    
    # Verify thought file exists and contains correct content
    thought_dir = os.path.join(ACTIVE_TASKS_DIR, task_id, "thoughts")
    thought_files = os.listdir(thought_dir)
    assert len(thought_files) == 1
    
    with open(os.path.join(thought_dir, thought_files[0])) as f:
        saved_thought = f.read()
    assert saved_thought == thought

def test_get_highest_priority_task(clean_task_dirs):
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
    assert highest_task is not None
    assert highest_task["priority"] == 2  # Task3 should be highest priority now
    assert highest_task["title"] == "Task 3"

def test_create_subtask(clean_task_dirs):
    """Test creating subtasks"""
    ensure_task_directories()
    
    # Create parent task
    parent_id = create_task("Parent task", "Parent description", priority=2)
    
    # Create subtask
    subtask_id = create_subtask(parent_id, "Subtask", "Subtask description")
    
    # Verify subtask
    subtask_data = get_task(subtask_id)
    assert subtask_data["parent_task"] == parent_id
    assert subtask_data["priority"] == 2  # Should inherit parent priority
    assert subtask_data["title"] == "Subtask"

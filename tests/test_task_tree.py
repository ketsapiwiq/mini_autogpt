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
    task_file = os.path.join(ACTIVE_TASKS_DIR, f"{task_id}.json")
    assert os.path.exists(task_file)
    
    # Verify task content
    with open(task_file) as f:
        task_data = json.load(f)
    
    assert task_data["title"] == "Test task"
    assert task_data["description"] == "Test description"
    assert task_data["priority"] == 2
    assert task_data["source"] == "test"

def test_get_task(clean_task_dirs):
    """Test retrieving task data"""
    ensure_task_directories()
    task_id = create_task(title="Test task", description="Test description")
    
    task_data = get_task(task_id)
    assert task_data["title"] == "Test task"
    assert task_data["description"] == "Test description"

def test_update_task_status(clean_task_dirs):
    """Test updating task status"""
    ensure_task_directories()
    task_id = create_task(title="Test task", description="Test description")
    
    # Update to in_progress
    update_task_status(task_id, "in_progress")
    task_data = get_task(task_id)
    assert task_data["status"] == "in_progress"
    
    # Update to completed with results
    results = {"result": "success"}
    update_task_status(task_id, "completed", results)
    task_data = get_task(task_id)
    assert task_data["status"] == "completed"
    assert task_data["results"] == results
    assert os.path.exists(os.path.join(COMPLETED_TASKS_DIR, f"{task_id}.json"))
    assert not os.path.exists(os.path.join(ACTIVE_TASKS_DIR, f"{task_id}.json"))

def test_add_thought(clean_task_dirs):
    """Test adding thoughts to a task"""
    ensure_task_directories()
    task_id = create_task(title="Test task", description="Test description")
    
    thought = "This is a test thought"
    add_thought(task_id, thought)
    
    task_data = get_task(task_id)
    assert "thoughts" in task_data
    assert thought in task_data["thoughts"]

def test_get_highest_priority_task(clean_task_dirs):
    """Test retrieving highest priority task"""
    ensure_task_directories()
    
    # Create tasks with different priorities
    task1_id = create_task(title="Task 1", description="Description 1", priority=3)
    task2_id = create_task(title="Task 2", description="Description 2", priority=1)  # Highest priority
    task3_id = create_task(title="Task 3", description="Description 3", priority=2)
    
    # Get highest priority task (should be task2)
    highest_task = get_highest_priority_task()
    assert highest_task is not None
    assert highest_task["priority"] == 1
    assert highest_task["title"] == "Task 2"
    
    # Complete task2 and verify task3 becomes highest priority
    update_task_status(task2_id, "completed")
    highest_task = get_highest_priority_task()
    assert highest_task is not None
    assert highest_task["priority"] == 2
    assert highest_task["title"] == "Task 3"

def test_create_subtask(clean_task_dirs):
    """Test creating subtasks"""
    ensure_task_directories()
    
    # Create parent task
    parent_id = create_task(title="Parent task", description="Parent description", priority=2)
    
    # Create subtask
    subtask_id = create_subtask(parent_id, "Subtask", "Subtask description")
    
    # Verify subtask was created
    subtask = get_task(subtask_id)
    assert subtask["title"] == "Subtask"
    assert subtask["description"] == "Subtask description"
    assert subtask["priority"] == 2  # Should inherit parent's priority
    assert subtask["parent_id"] == parent_id

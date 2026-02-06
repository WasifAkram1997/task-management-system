"""
Tests for Task Service endpoints
"""

import pytest
import uuid
from faker import Faker

fake = Faker()


# Helper fixture for authenticated headers
@pytest.fixture
def auth_headers():
    """Mock authenticated user headers"""
    return {
        "X-User-ID": str(uuid.uuid4()),
        "X-User-Email": "test@example.com"
    }


# ==================== Health Check ====================

def test_health_check(client):
    """Test health check endpoint"""
    response = client.get("/health")
    
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


# ==================== Create Task ====================

def test_create_task(client, auth_headers):
    """Test creating a task"""
    task_data = {
        "title": "Test Task",
        "description": "Test Description",
        "priority": "HIGH",
        "status": "TODO"
    }
    
    response = client.post("/tasks", json=task_data, headers=auth_headers)
    
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test Task"
    assert data["description"] == "Test Description"
    assert data["priority"] == "HIGH"
    assert data["status"] == "TODO"
    assert "id" in data
    assert "created_by" in data


def test_create_task_minimal(client, auth_headers):
    """Test creating task with only required fields"""
    task_data = {
        "title": "Minimal Task"
    }
    
    response = client.post("/tasks", json=task_data, headers=auth_headers)
    
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Minimal Task"
    assert data["status"] == "TODO"  # Default
    assert data["priority"] == "MEDIUM"  # Default


def test_create_task_no_auth(client):
    """Test creating task without authentication fails"""
    task_data = {
        "title": "Test Task"
    }
    
    response = client.post("/tasks", json=task_data)
    
    assert response.status_code == 401


# ==================== List Tasks ====================

def test_list_tasks(client, auth_headers):
    """Test listing all tasks"""
    # Create some tasks first
    client.post("/tasks", json={"title": "Task 1"}, headers=auth_headers)
    client.post("/tasks", json={"title": "Task 2"}, headers=auth_headers)
    
    response = client.get("/tasks", headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 2


def test_list_tasks_filter_by_status(client, auth_headers):
    """Test filtering tasks by status"""
    # Create tasks with different statuses
    client.post("/tasks", json={"title": "Todo Task", "status": "TODO"}, headers=auth_headers)
    client.post("/tasks", json={"title": "Done Task", "status": "DONE"}, headers=auth_headers)
    
    response = client.get("/tasks?status_filter=TODO", headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    for task in data:
        assert task["status"] == "TODO"


def test_list_tasks_filter_by_priority(client, auth_headers):
    """Test filtering tasks by priority"""
    client.post("/tasks", json={"title": "High Priority", "priority": "HIGH"}, headers=auth_headers)
    client.post("/tasks", json={"title": "Low Priority", "priority": "LOW"}, headers=auth_headers)
    
    response = client.get("/tasks?priority=HIGH", headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    for task in data:
        assert task["priority"] == "HIGH"


# ==================== Get Single Task ====================

def test_get_task(client, auth_headers):
    """Test getting a specific task"""
    # Create a task
    create_response = client.post("/tasks", json={"title": "Get This Task"}, headers=auth_headers)
    task_id = create_response.json()["id"]
    
    # Get the task
    response = client.get(f"/tasks/{task_id}", headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == task_id
    assert data["title"] == "Get This Task"


def test_get_task_not_found(client, auth_headers):
    """Test getting non-existent task returns 404"""
    fake_id = str(uuid.uuid4())
    
    response = client.get(f"/tasks/{fake_id}", headers=auth_headers)
    
    assert response.status_code == 404


# ==================== Update Task ====================

def test_update_task(client, auth_headers):
    """Test updating a task"""
    # Create a task
    create_response = client.post("/tasks", json={"title": "Original Title"}, headers=auth_headers)
    task_id = create_response.json()["id"]
    
    # Update the task
    update_data = {
        "title": "Updated Title",
        "status": "IN_PROGRESS",
        "priority": "CRITICAL"
    }
    response = client.put(f"/tasks/{task_id}", json=update_data, headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated Title"
    assert data["status"] == "IN_PROGRESS"
    assert data["priority"] == "CRITICAL"


def test_update_task_partial(client, auth_headers):
    """Test partial update of task"""
    # Create a task
    create_response = client.post("/tasks", json={
        "title": "Original",
        "description": "Original Description"
    }, headers=auth_headers)
    task_id = create_response.json()["id"]
    
    # Update only title
    update_data = {"title": "New Title"}
    response = client.put(f"/tasks/{task_id}", json=update_data, headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "New Title"
    assert data["description"] == "Original Description"  # Unchanged


def test_update_task_not_found(client, auth_headers):
    """Test updating non-existent task returns 404"""
    fake_id = str(uuid.uuid4())
    
    response = client.put(f"/tasks/{fake_id}", json={"title": "New"}, headers=auth_headers)
    
    assert response.status_code == 404


# ==================== Delete Task ====================

def test_delete_task(client, auth_headers):
    """Test deleting a task"""
    # Create a task
    create_response = client.post("/tasks", json={"title": "Delete Me"}, headers=auth_headers)
    task_id = create_response.json()["id"]
    
    # Delete the task
    response = client.delete(f"/tasks/{task_id}", headers=auth_headers)
    
    assert response.status_code == 204
    
    # Verify it's deleted
    get_response = client.get(f"/tasks/{task_id}", headers=auth_headers)
    assert get_response.status_code == 404


def test_delete_task_not_found(client, auth_headers):
    """Test deleting non-existent task returns 404"""
    fake_id = str(uuid.uuid4())
    
    response = client.delete(f"/tasks/{fake_id}", headers=auth_headers)
    
    assert response.status_code == 404


# ==================== Comments ====================

def test_add_comment(client, auth_headers):
    """Test adding a comment to a task"""
    # Create a task
    create_response = client.post("/tasks", json={"title": "Task with Comments"}, headers=auth_headers)
    task_id = create_response.json()["id"]
    
    # Add comment
    comment_data = {"content": "This is a test comment"}
    response = client.post(f"/tasks/{task_id}/comments", json=comment_data, headers=auth_headers)
    
    assert response.status_code == 201
    data = response.json()
    assert data["content"] == "This is a test comment"
    assert data["task_id"] == task_id
    assert "id" in data


def test_add_comment_task_not_found(client, auth_headers):
    """Test adding comment to non-existent task fails"""
    fake_id = str(uuid.uuid4())
    
    comment_data = {"content": "Comment"}
    response = client.post(f"/tasks/{fake_id}/comments", json=comment_data, headers=auth_headers)
    
    assert response.status_code == 404


def test_list_comments(client, auth_headers):
    """Test listing comments for a task"""
    # Create a task
    create_response = client.post("/tasks", json={"title": "Task"}, headers=auth_headers)
    task_id = create_response.json()["id"]
    
    # Add comments
    client.post(f"/tasks/{task_id}/comments", json={"content": "Comment 1"}, headers=auth_headers)
    client.post(f"/tasks/{task_id}/comments", json={"content": "Comment 2"}, headers=auth_headers)
    
    # List comments
    response = client.get(f"/tasks/{task_id}/comments", headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2


def test_list_comments_task_not_found(client, auth_headers):
    """Test listing comments for non-existent task fails"""
    fake_id = str(uuid.uuid4())
    
    response = client.get(f"/tasks/{fake_id}/comments", headers=auth_headers)
    
    assert response.status_code == 404
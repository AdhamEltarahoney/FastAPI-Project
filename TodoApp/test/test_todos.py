from fastapi import status
from TodoApp.routers.todos import get_db, get_current_user
from ..models import Todos
from .utils import *
# Database URL for testing



# Apply dependency overrides
app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user

# Create a TestClient instance for FastAPI

@pytest.fixture
def test_todo():
    todo = Todos(title="Test Todo", description="Test Description", priority= 5, complete = False, owner_id = 1)
    db = TestingSessionLocal()
    db.add(todo)
    db.commit()
    yield db
    with engine.connect() as connection:
        connection.execute(text("DELETE FROM todos"))
        connection.commit()
 
# Test function for authenticated route
def test_read_all_authenticated(test_todo):
    response = client.get("/todos")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [{"id": 1,"title": "Test Todo","description": "Test Description","priority": 5,"complete": False, "owner_id": 1}]

def test_read_one_authenticated(test_todo):
    response = client.get("/todos/todo/1")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"id": 1,"title": "Test Todo","description": "Test Description","priority": 5,"complete": False, "owner_id": 1}


def test_read_one_authenticated_not_found(test_todo):
    response = client.get("/todos/todo/9909090909")
    assert response.status_code == 404
    assert response.json() == {"detail": "Todo not found"}


def test_create_todo(test_todo):
    request_data = {
        'title': 'Test Todo',
        'description': 'Test Description',
        'priority': 5,
        'complete': False,
    }
    response = client.post('/todos/todo', json=request_data)
    assert response.status_code == 201

    db = TestingSessionLocal()
    model = db.query(Todos).filter(Todos.title == 'Test Todo').first()
    assert model.title == 'Test Todo'
    assert model.description == 'Test Description'
    assert model.priority == 5
    assert model.complete == False
    assert model.owner_id == 1 

def test_update_todo(test_todo):
    request_data = {
        'title': 'Test Todo',
        'description': 'Test Description',
        'priority': 5,
        'complete': False,
    }
    response = client.put('/todos/todo/1', json=request_data)
    assert response.status_code == 204
    db = TestingSessionLocal()
    model = db.query(Todos).filter(Todos.id == 1).first()
    assert model.title  == "Test Todo"
  

def test_update_todo_not_found(test_todo):
    request_data = {
         'title':  'Test Todo',
         'description':  'Test Description',
         'priority': 5,
         'complete': False,
    }
    response = client.put('/todos/todo/999', json=request_data)
    assert response.status_code == 404
    assert response.json() == {"detail": "not found"}


def test_delete_todo(test_todo):
    response = client.delete('/todos/todo/1')
    assert response.status_code == 204
    db = TestingSessionLocal()
    model = db.query(Todos).filter(Todos.id == 1).first()
    assert model is None

def test_delete_todo_not_found(test_todo):
    response = client.delete('/todos/todo/999')
    assert response.status_code == 404
    assert response.json() ==  {"detail": "Todo not found"}
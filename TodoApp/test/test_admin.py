from .utils import *
from ..routers.admin import get_current_user, get_db
from fastapi import status
from ..models import Todos


app.dependency_overrides[get_current_user] = override_get_current_user
app.dependency_overrides[get_db] = override_get_db


def test_admin_read_all_authenticated(test_todo):
    response = client.get("/auth/todo")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [{"id": 1,"title": "Test Todo","description": "Test Description","priority": 5,"complete": False, "owner_id": 1}]


def test_admin_delete_todo(test_todo):
    response = client.delete("/auth/todo/1")
    
    assert response.status_code == 204

    db = TestingSessionLocal()
    model = db.query(Todos).filter(Todos.id == 1).first()
    assert model is None


def test_delete_todo_not_found():
    response =  client.delete("/auth/todo/999")
    assert response.status_code == 401
    assert response.json() == {"detail": "Todo not found"}

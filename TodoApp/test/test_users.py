from .utils import *
from ..routers.users import get_db, get_current_user
from fastapi import status

app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user


def test_return_user(test_user):
    response = client.get("/user")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "id": test_user.id,
        "username": test_user.username,
        "email": test_user.email,
        "first_name": test_user.first_name,
        "last_name": test_user.last_name,
        "role": test_user.role,
        "hashed_password": test_user.hashed_password,
        "is_active": test_user.is_active,
    }



def test_change_password_success(test_user):
    response = client.put("/user/password", json={"password": "testpassword",  # Use actual password
                                                  "new_password": "newpassword"})
    assert response.status_code == status.HTTP_204_NO_CONTENT


def test_change_password_invalid_current_password(test_user):
    response = client.put("/user/password", json={"password": "wrongpassword",
                                                  "new_password": "newpassword"})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED  # or HTTP_404_NOT_FOUND if intended
    assert response.json() == {"detail": 'Error on password change'}



from datetime import timedelta
import pytest
import jwt
from .utils import *
from ..routers.auth import ALGORTHM, SECRET_KEY, create_access_token, get_db, authenticate_user, get_current_user
from fastapi import HTTPException

app.dependency_overrides[get_db] = override_get_db


def test_authenticate_user(test_user):
    db = TestingSessionLocal()
    authenticated_user = authenticate_user(test_user.username, 'testpassword', db)
    assert authenticated_user is not None
    assert authenticated_user.username == test_user.username

    non_existant_user = authenticate_user('wrongusername', 'testuser', db)
    assert non_existant_user is False

    wrong_pass = authenticate_user(test_user.username, 'dedoin', db)
    assert wrong_pass is False


def test_create_access_token():
    username = 'testuser'
    user_id = 1
    role = 'user'
    expires_delta = timedelta(days=1)
    
    token = create_access_token(username = username, user_id = user_id, role = role, expires_delta = expires_delta)

    decoded_token = jwt.decode(token, SECRET_KEY, algorithms=[ALGORTHM], options={'verify_signature':False})
    assert decoded_token['sub'] == username
    assert decoded_token['id'] == user_id
    assert decoded_token['role'] == role


#pytest cannot test async unless you use pytest.mark.asyncio
@pytest.mark.asyncio
async def test_get_current_user_get_current_user_token():
    encode = {'sub' : 'testuser', 'id': 1, 'role': 'admin'}
    token = jwt.encode(encode, SECRET_KEY, algorithm=ALGORTHM)

    user = await get_current_user(token=token)
    assert user == {'username': 'testuser', 'id': 1, 'role': 'admin'}


@pytest.mark.asyncio
async def test_get_current_user_missing_payload():
    encode = {'role': 'user'}
    token = jwt.encode(encode, SECRET_KEY, algorithm=ALGORTHM)
    
    with pytest.raises(HTTPException) as excinfo:
        await get_current_user(token=token)
    
    assert excinfo.value.status_code == 401
    assert excinfo.value.detail == 'could not validate user'
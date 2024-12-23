from datetime import datetime, timedelta, timezone
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from pytest import Session
from ..models import Users
from passlib.context import CryptContext
from ..database import SessionLocal
from starlette import status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import JWTError, jwt
from fastapi.templating import Jinja2Templates

router = APIRouter(prefix='/auth',
                   tags=['auth']
                   )

SECRET_KEY = '49df2552092cd16502892602476548d9ec1fb1f05f55d5e4e8496a0ccd5e81f7'
ALGORTHM = 'HS256'

bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
oauth2_bearer = OAuth2PasswordBearer(tokenUrl='auth/token')

#JWT - Header (a), Payload(b) and a Signature(c)
#Header - Algorithm and type of token
#Payload, data which contains claims like registered(ISS, Subject, exp), public and private
#signature , created by algorithm in header can be anything saved on the server





class CreateUserRequest(BaseModel):
    username: str
    email: str
    first_name: str
    last_name: str
    password: str
    role: str
    


class Tokeb(BaseModel):
    access_token: str
    token_type: str



def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependancy = Annotated[Session, Depends(get_db)]
templates = Jinja2Templates(directory="TodoApp/templates")

###pages###
@router.get("/login-page")
def render_login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@router.get("/register-page")
def render_register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

###endpoints


def authenticate_user(Username: str, password: str, db):
    user = db.query(Users).filter(Users.username == Username).first()
    if not user:
        return False
    if not bcrypt_context.verify(password, user.hashed_password):
        return False
    return user



def create_access_token(username: str, user_id: int, role: str, expires_delta: timedelta):
    # Payload to encode
    encode = {'sub': username, 'id': user_id, 'role': role}
    
    # Set expiration time
    expires = datetime.now(timezone.utc) + expires_delta
    encode.update({'exp': expires})
    
    # Encode JWT
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORTHM)


async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORTHM])
        username: str = payload.get('sub')
        user_id: int = payload.get('id')
        user_role: str = payload.get('role')
        if username is None or user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail = 'could not validate user')
        return {'username': username, 'id':user_id, 'role':user_role}
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail = 'could not validate user')



@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(db: db_dependancy, create_user_request : CreateUserRequest):

    create_user_model = Users(
        email=create_user_request.email,
        username = create_user_request.username,
        first_name = create_user_request.first_name,
        last_name = create_user_request.last_name,
        role = create_user_request.role,
        hashed_password = bcrypt_context.hash(create_user_request.password),
        is_active = True,
    )
    db.add(create_user_model)
    db.commit()


    return {
        create_user_model 
    }




@router.post("/token", response_model=Tokeb)
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: db_dependancy):
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:     
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail = 'could not validate user')
    token = create_access_token(user.username, user.role, user.id, timedelta(minutes=20))
    
    return {'access_token': token, 'token_type': 'bearer'}
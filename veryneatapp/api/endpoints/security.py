"""
Let's imagine that you have your backend API in some domain.
And you have a frontend in another domain or in a different path of the same domain (or in a mobile application).
And you want to have a way for the frontend to authenticate with the backend, using a username and password.
We can use OAuth2 to build that with FastAPI.

OAuth2 was designed so that the backend or API could be independent of the server that authenticates the user.
But in this case (example below), the same FastAPI application will handle the API and the authentication.

Simplified flow:
1. The user types the username and password in the frontend
2. The frontend (running in the user's browser) sends credentials to our API (declared with tokenUrl="token")
3. The API checks that username and password, and responds with a temporary "token" (which can be used to verify user)
4. The frontend stores that token temporarily somewhere.
5. The user clicks in the frontend to go to another section of the frontend web app.
6. The frontend needs to fetch some more data from a secured API endpointdatetime A combination of a date and a time. Attributes: ()
   a. To authenticate with our API, the frontend sends a header Authorization="Bearer"+ " " + <token>.
"""
from datetime import datetime, timedelta
from typing import Dict

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext

from veryneatapp.api.schemas.token import Token, TokenPayload
from veryneatapp.api.schemas.user import User, UserInDB

router = APIRouter()


# to get a string like this run:
# openssl rand -hex 32
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


fake_users_db = {
    "johndoe": {
        "username": "johndoe",
        "full_name": "John Doe",
        "email": "johndoe@example.com",
        "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # hashed version of `secret`
        "is_active": True,
        "is_superuser": False,
    }
}

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# tokenUrl parameter contains the URL that the client should use to get the token.
# As it's a relative URL, it's equivalent to ./token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str):
    return pwd_context.hash(password)


def get_user(db: Dict, username: str):
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)


def authenticate_user(fake_db: Dict, username: str, password: str):
    user = get_user(fake_db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(
    data: Dict, expires_delta: timedelta = timedelta(minutes=15)
):
    """utility function to generate a new access token."""
    to_encode = data.copy()
    to_encode.update({"exp": datetime.utcnow() + expires_delta})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2_scheme)):
    """
    Looks in the request for the Authorization header, check if the value is Bearer plus some token, 
    and will return the token as a str.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload: dict = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenPayload(username=username)
    except JWTError:
        raise credentials_exception
    user = get_user(fake_users_db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
):
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
):
    """
    Create a real JWT access token with a given timedelta, and return it.
    The `sub` key is optional, but that's where we'd put the user/object/whatever identification
    """
    user = authenticate_user(
        fake_users_db, form_data.username, form_data.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("security/users/me")
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    """
    Displays the current user, that was retrieved directly from the path operation as a dependency
    authenticate with `johndoe` and `secret`
    """
    return current_user


@router.get("security/users/me/items/")
async def read_own_items(current_user: User = Depends(get_current_active_user)):
    """
    Displays the logged in user's personal data
    authenticate with `johndoe` and `secret`
    """
    return [{"item_id": "Foo", "owner": current_user.username}]

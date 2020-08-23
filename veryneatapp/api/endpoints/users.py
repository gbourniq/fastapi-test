from fastapi import APIRouter, status, Depends
from veryneatapp.api.schemas.user import UserCreate, UserOut, UserInDB
from veryneatapp.api.dependencies.core_dependencies import (
    DummyUserManagementExample,
)

router = APIRouter()


# Fake routes
@router.get("/users/")
async def read_users():
    return [{"username": "Foo"}, {"username": "Bar"}]


@router.get("/users/me")
async def read_user_me():
    return {"username": "fakecurrentuser"}


@router.get("/users/{username}")
async def read_user(username: str):
    return {"username": username}


# very simplified user management
# check security.py for a real example
@router.post(
    "/fake-create-user/",
    response_model=UserOut,
    status_code=status.HTTP_201_CREATED,
)
async def create_user(user_saved: UserInDB = Depends(DummyUserManagementExample.fake_save_user)):
    """
    Here, user_saved contains the password
    but because we specify response_model=UserOut which does NOT
    contain the pwd, then it will be filtered out in the final response
    """
    return user_saved

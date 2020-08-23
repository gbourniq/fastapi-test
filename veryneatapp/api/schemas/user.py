from typing import Optional

from pydantic import BaseModel, EmailStr

# class User(BaseModel):
#     """
#     Pydantic data model for Item, to be passed through the request body
#     """

#     username: str = Field(..., example="moyne.zoy")
#     full_name: Optional[str] = Field(
#         None, description="User full name", max_length=50, example="Moyne Zoy"
#     )


# for DB operations
# Shared properties
class UserBase(BaseModel):
    username: str
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = True
    is_superuser: bool = False


class User(UserBase):
    pass


class UserOut(UserBase):
    pass


# Properties to receive via API on creation
class UserCreate(UserBase):
    email: EmailStr
    password: str


# Properties to receive via API on update
class UserUpdate(UserBase):
    password: Optional[str] = None


class UserInDBBase(UserBase):
    id: Optional[int] = None

    class Config:
        orm_mode = True


# Additional properties to return via API
# class User(UserInDBBase):
#     pass


# Additional properties stored in DB
class UserInDB(UserInDBBase):
    hashed_password: str

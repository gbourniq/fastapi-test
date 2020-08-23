from typing import Dict, List, Optional, Union, Set

from pydantic import BaseModel, EmailStr, Field, HttpUrl


class Image(BaseModel):
    url: HttpUrl
    name: str


class BaseItem(BaseModel):
    name: str = Field(..., example="Foo")
    description: Optional[str] = Field(None, example="A very nice Item")


class SimpleItem(BaseItem):
    pass


class Item(BaseItem):
    price: float = Field(..., ge=0, le=1000, example=35.4)
    tax: Optional[float] = Field(default=0.1, example=3.2)
    tags: Set[str] = Field(set(), example=["blue", "green"])


class ItemWithImage(Item):
    images: Optional[List[Image]] = Field(
        None, example=["http://my-image-url.com"]
    )


class CarItem(BaseItem):
    type = "car"


class PlaneItem(BaseItem):
    type = "plane"
    size: int


# Items for DB operations
# Shared properties
class ItemBase(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    type: str = None


# Properties to receive on item creation
class ItemCreate(ItemBase):
    title: str


# Properties to receive on item update
class ItemUpdate(ItemBase):
    pass


# Properties shared by models stored in DB
class ItemInDBBase(ItemBase):
    id: int
    title: str
    owner_id: int

    class Config:
        orm_mode = True


# Properties to return to client
class ItemOutDB(ItemInDBBase):
    pass


# Properties properties stored in DB
class ItemInDB(ItemInDBBase):
    pass

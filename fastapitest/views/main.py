from fastapi import Request, Cookie, status, HTTPException
from typing import Dict, Optional, List, Union
from fastapitest import app, templates
from pydantic import BaseModel, Field, HttpUrl, EmailStr
from fastapi.responses import JSONResponse

@app.get("/")
async def index(request: Request):
    """
    GET route which returns HTML template,
    run curl http://0.0.0.0:5700/
    """
    return templates.TemplateResponse(
        "index.html", context={"request": request}
    )


@app.get("/tutorial")
async def tutorial():
    """This is a simple GET route, to use this
    run curl http://0.0.0.0:5700/tutorial
    """
    return {"message": {"this is another route"}}


@app.post("/index-weights/")
async def create_index_weights(weights: Dict[int, float]):
    """
    Request body to accept any dict as long as it has int keys with float values
    The request body sent by the client is expected to be in the form of:
        {"129385": 1.45}
    """
    return weights

@app.get("/cookie-example/")
async def read_items(ads_id: Optional[str] = Cookie(None)):
    """Cookie example
    declare the cookie parameters using the same structure as with Path and Query.
    The first value is the default value, you can pass all the extra validation or annotation parameters
    """
    return {"ads_id": ads_id}


# Returns model data (1 pydantic model)
# FastAPI will take care of filtering out all the data that is not declared in the output model (using Pydantic)
class UserBase(BaseModel):
    username: str
    email: EmailStr
    full_name: Optional[str] = None


class UserIn(UserBase):
    password: str


class UserOut(UserBase):
    pass


class UserInDB(UserBase):
    hashed_password: str


def fake_password_hasher(raw_password: str):
    return "supersecret" + raw_password


def fake_save_user(user_in: UserIn):
    hashed_password = fake_password_hasher(user_in.password)
    user_in_db = UserInDB(**user_in.dict(), hashed_password=hashed_password)
    print("User saved! ..not really")
    return user_in_db


@app.post("/response-model-sample/create-user/", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def create_user(user_in: UserIn):
    user_saved = fake_save_user(user_in)
    return user_saved




# Returns List of models
class SimpleItem(BaseModel):
    name: str
    description: str


items = [
    {"name": "Foo", "description": "There comes my hero"},
    {"name": "Red", "description": "It's my aeroplane"},
]


@app.get("/response-model-sample-list/items/", response_model=List[SimpleItem])
async def read_items():
    return items


# Can return different data models with Union, 
# Eg. `response_model=Union[PlaneItem, CarItem]` allows to return both schemas

# + Exception handling 404, with optional headers
class BaseItem(BaseModel):
    description: str
    type: str


class CarItem(BaseItem):
    type = "car"


class PlaneItem(BaseItem):
    type = "plane"
    size: int


items = {
    "item1": {"description": "All my friends drive a low rider", "type": "car"},
    "item2": {
        "description": "Music is my aeroplane, it's my aeroplane",
        "type": "plane",
        "size": 5,
    },
}

@app.get("/get-item-or-404/{item_id}", response_model=Union[PlaneItem, CarItem], status_code=status.HTTP_200_OK)
async def read_item(item_id: str):
    if item_id not in items:
        raise HTTPException(status_code=404, detail="Oooooops.. Item not found", headers={"X-Error": "There goes my error"})
    return items[item_id]


# Response with arbitrary dict
@app.get("/keyword-weights/", response_model=Dict[str, float])
async def read_keyword_weights():
    return {"foo": 2.3, "bar": 3.4}


# Custom Exception Handling

class UnicornException(Exception):
    def __init__(self, name: str):
        self.name = name


@app.exception_handler(UnicornException)
async def unicorn_exception_handler(request: Request, exc: UnicornException):
    return JSONResponse(
        status_code=418,
        content={"message": f"Oops! {exc.name} did something. There goes a rainbow..."},
    )


@app.get("/custom-exception-handler-unicorns/{name}")
async def read_unicorn(name: str):
    """
    Pass `yolo` as the path parameter to trigger the exception
    """
    if name == "yolo":
        raise UnicornException(name=name)
    return {"unicorn_name": name}

# More error handling info here https://fastapi.tiangolo.com/tutorial/handling-errors/

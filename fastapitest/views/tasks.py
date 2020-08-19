from time import sleep
from datetime import datetime, time, timedelta
from typing import Optional, Dict, List, Set
from enum import Enum

from uuid import UUID

from fastapi import (
    BackgroundTasks,
    Query,
    Path,
    Body,
    Header,
    status,
    Form,
    File,
    UploadFile,
    HTTPException,
    Depends,
    Cookie
)
from fastapi.responses import HTMLResponse
from fastapi.encoders import jsonable_encoder

from pydantic import BaseModel, Field, HttpUrl, EmailStr

from fastapitest import app


class ModelName(str, Enum):
    """
    Enum which set a number of model names which
    can be seleted as query/path parameters
    """

    alexnet = "alexnet"
    resnet = "resnet"
    lenet = "lenet"


class User(BaseModel):
    """
    Pydantic data model for Item, to be passed through the request body
    """

    username: str = Field(..., example="moyne.zoy")
    full_name: Optional[str] = Field(
        None, description="User full name", max_length=50, example="Moyne Zoy"
    )


class Image(BaseModel):
    url: HttpUrl
    name: str


class Item(BaseModel):
    """
    Pydantic data model for User, to be passed through the request body
    """

    name: str = Field(..., example="Foo")
    description: Optional[str] = Field(None, example="A very nice Item")
    price: float = Field(..., ge=0, le=1000, example=35.4)
    tax: Optional[float] = Field(default=0.1, example=3.2)
    tags: Set[str] = Field(set(), example=["blue", "green"])
    images: Optional[List[Image]] = Field(
        None, example=["http://my-image-url.com"]
    )


def _task_run(
    item: Dict, model_name: str, task_name: str, task_id: Optional[int] = None
) -> None:
    """Private function to simulate an heavy I/O operation

    Args:
        task_name (str): name of the task
        task_id (int, optional): id of the task
        
    Output:
        append data to log file
    """
    sleep(3)  # simulates heavy I/O
    with open("task_out.txt", mode="a") as f:
        content = f"{item} | {model_name} | {task_name} | {task_id} | {datetime.now()}\n"
        f.write(content)


@app.post(
    "/task/run/{task_id}",
    status_code=status.HTTP_200_OK,
    tags=["Asynchronous Tasks"],
)
async def task_run(
    model_name: ModelName,
    background_tasks: BackgroundTasks,
    item: Item = Body(..., embed=True),
    user: User = Body(..., embed=True),
    importance: int = Body(..., ge=0, le=5, example=3),
    task_id: int = Path(..., description="The ID of the task to run", le=1000),
    task_name: str = Query(
        ...,
        title="Query string",
        description="Query string for the task name",
        alias="task-name",
        max_length=50,
        regex="^.*$",
    ),
    dry_run: Optional[bool] = False,
) -> Dict:
    """
    Async function that takes in a task and writes into a file
    by calling the background task `_task_run`

    - **model_name** (Required query param): Name of the model to be selected from the downdown list
    - **item** (Required request body): Item data (defined by the pydantic data model)
    - **user** (Required request body): User data (defined by the pydantic data model)
    - **importance** (Required request body): Integer to flag task importance
    - **task_id** (Required path param): Task ID
    - **task_name** (Required query param): Task name
    - **dry_run** (Optional query param): Set to True prevent asynchronous from actually running
    """

    req_data = f"User: {user.full_name} | Item: {item.name} | Model: {model_name.value} | Task: {task_name} | Task ID: {task_id}, is being run..."

    if not dry_run:
        background_tasks.add_task(
            _task_run, item, model_name.value, task_name, task_id
        )
        return {"message": req_data}
    return {"message": f"Dry run enabled for {req_data}"}


@app.put("/advanced-datatypes/{item_id}", status_code=status.HTTP_200_OK)
async def advanced_datatypes(
    item_id: UUID = Path(..., example="123e4567-e89b-12d3-a456-426614174000"),
    start_datetime: Optional[datetime] = Body(
        None, example="2020-08-18T14:38:07.741Z"
    ),
    end_datetime: Optional[datetime] = Body(
        None, example="2020-08-18T14:40:07.741Z"
    ),
    repeat_at: Optional[time] = Body(None, example="14:23:55.003"),
    process_after: Optional[timedelta] = Body(None, example="11.03"),
):
    """
    Route to show some advanced data types: UUID, datetime, time, timedelta
    """
    start_process = start_datetime + process_after
    duration = end_datetime - start_process
    return {
        "item_id": item_id,
        "start_datetime": start_datetime,
        "end_datetime": end_datetime,
        "repeat_at": repeat_at,
        "process_after": process_after,
        "start_process": start_process,
        "duration": duration,
    }


@app.get("/header-sample/", status_code=status.HTTP_200_OK)
async def header_sample(user_agent: Optional[str] = Header(None)):
    return {"User-Agent": user_agent}


@app.post("/login-with-form-parameters/")
async def login_with_form_params(
    username: str = Form(...), password: str = Form(...)
):
    return {"username": username}


# Upload File via /docs API page
# more info: https://fastapi.tiangolo.com/tutorial/request-files/


@app.post("/uploadfiles/")
async def create_upload_files(files: List[UploadFile] = File(...)):
    # need to implement saving / reading the file with file.read()
    return {"filenames": [file.filename for file in files]}


# Upload file via a web page
@app.get("/upload/")
async def main():
    content = """
<body>
<form action="/files/" enctype="multipart/form-data" method="post">
<input name="files" type="file" multiple>
<input type="submit">
</form>
<form action="/uploadfiles/" enctype="multipart/form-data" method="post">
<input name="files" type="file" multiple>
<input type="submit">
</form>
</body>
    """
    return HTMLResponse(content=content)


# Upload file and form
@app.post("/upload-files-and-form-data/")
async def create_file(
    file: bytes = File(...),
    fileb: UploadFile = File(...),
    token: str = Form(...),
    dummy_query_string: str = Query(None),
):
    return {
        "file_size": len(file),
        "token": token,
        "fileb_content_type": fileb.content_type,
    }


# PUT is used to replace existing data
# All the fields must be specified! Or default values will be used to override existing fields

# Update model data with PUT and jsonable_encoder
# This is comparable to using the model's .dict() method,
# but it makes sure (and converts) the values to data types that can be converted to JSON
# for example, datetime to str
class SimpleItem(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    tax: float = 10.5
    tags: List[str] = []


items = {
    "foo": {"name": "Foo", "price": 50.2},
    "bar": {
        "name": "Bar",
        "description": "The bartenders",
        "price": 62,
        "tax": 20.2,
    },
    "baz": {
        "name": "Baz",
        "description": None,
        "price": 50.2,
        "tax": 10.5,
        "tags": [],
    },
}


@app.get("/get-items/{item_id}", response_model=SimpleItem)
async def read_item(item_id: str):
    if item_id not in items:
        raise HTTPException(
            status_code=404,
            detail="Oooooops.. Item not found",
            headers={"X-Error": "There goes my error"},
        )
    return items[item_id]


@app.put("/update/items/{item_id}", response_model=SimpleItem)
async def update_item(item_id: str, item: SimpleItem):
    update_item_encoded = item.dict()
    items[item_id] = update_item_encoded
    return update_item_encoded


# Use PATCH to update specific fields (Partial updates)
# item.dict(exclude_unset=True) to generate a dict with only the data
# that was set (sent in the request), omitting default values
@app.patch("/items/{item_id}", response_model=Item)
async def update_item(item_id: str, item: Item):
    stored_item_data = items[item_id]
    stored_item_model = Item(**stored_item_data)
    update_data = item.dict(exclude_unset=True)
    updated_item = stored_item_model.copy(update=update_data)
    items[item_id] = jsonable_encoder(updated_item)
    return updated_item


# DEPENDENCIES
# "Dependency Injection" means, in programming, that there is a way for your code
# (in this case, your path operation functions) to declare things that
# it requires to work and use: "dependencies". This minimizes code repetition!

"""
This is very useful when you need to:
- Have shared logic (the same code logic again and again).
- Share database connections.
- Enforce security, authentication, role requirements, etc.
- And many other things...

The simplicity of the dependency injection system makes FastAPI compatible with:
- all the relational databases
- NoSQL databases
- external packages
- external APIs
- authentication and authorization systems
- API usage monitoring systems
- response data injection systems
- etc.

All these dependencies, while declaring their requirements, 
also add parameters, validations, etc. to your path operations.
"""


class CommonQueryParams:
    """First dependency (must be callable)
    that expects 3 optional query parameters

    Args:
        q (str, optional). Defaults to None.
        skip (int, optional). Defaults to 0.
        limit (int, optional). Defaults to 100.

    Returns:
        (dict). dict containing those values
    """
    def __init__(self, q: Optional[str] = None, skip: int = 0, limit: int = 100):
        self.q = q
        self.skip = skip
        self.limit = limit



@app.get("/leverage-dep/")
async def read_items(commons: CommonQueryParams = Depends(CommonQueryParams)):
    """
    First route that leverage dependencies
    FastAPI calls the CommonQueryParams class. This creates an "instance" of that class
    and the instance will be passed as the parameter commons to your function.


    Whenever a new request arrives, FastAPI will take care of:
    - Calling your dependency ("dependable") function with the correct parameters.
    - Get the result from your function.
    - Assign that result to the parameter in your path operation function.
    - This way you write shared code once and FastAPI takes care of calling it for your path operations.
    """
    return commons


# Dependency use case
# If the user didn't provide any query q,
# we use the last query used, which we saved to a cookie before.

def query_extractor(q: Optional[str] = None):
    return q


def query_or_cookie_extractor(
    q: str = Depends(query_extractor), last_query: Optional[str] = Cookie(None)
):
    if not q:
        return last_query
    return q


@app.get("/query-or-cookie/")
async def read_query_or_cookie_extractor(query_or_default: str = Depends(query_or_cookie_extractor)):
    return {"q_or_cookie": query_or_default}


# For dependencies that dont return any values - with dependencies
async def verify_token(x_token: str = Header(default="fake-super-secret-token")):
    if x_token != "fake-super-secret-token":
        raise HTTPException(status_code=400, detail="X-Token header invalid")


async def verify_key(x_key: str = Header(default="fake-super-secret-key")):
    if x_key != "fake-super-secret-key":
        raise HTTPException(status_code=400, detail="X-Key header invalid")
    return x_key # won't be used because of dependencies


@app.get("/dependencies-no-returned-values/exception-handled/", dependencies=[Depends(verify_token), Depends(verify_key)])
async def read_items():
    return [{"item": "Foo"}, {"item": "Bar"}]

# Can use dependencies for a group of path operations (minimize code)


# Dependencies that do some extra steps after finishing (based on yield)
async def get_db():
    db = DBSession() # executed before sending a response 
    try:
        yield db # what is injected into the path operations and other dependencies
    finally:
        db.close() #  executed after the response has been delivered

# Other example
    """
    It might be tempting to raise an HTTPException or similar in the exit code, 
    AFTER the yield. But it won't work. because the request is already sent. (Can do it before only._
    If you have some code that you know could raise an exception, 
    do the most normal/"Pythonic" thing and add a try block in that section of the code.
    """
async def dependency_a():
    dep_a = generate_dep_a()
    try:
        yield dep_a
    finally:
        dep_a.close()


async def dependency_b(dep_a=Depends(dependency_a)):
    dep_b = generate_dep_b()
    try:
        yield dep_b
    finally:
        dep_b.close(dep_a) # 2. dependency_b needs the value from dependency_a (here named dep_a) to be available for its exit code.


async def dependency_c(dep_b=Depends(dependency_b)):
    dep_c = generate_dep_c()
    try:
        yield dep_c
    finally:
        dep_c.close(dep_b) # 1. dependency_c, to execute its exit code, needs the value from dependency_b (here named dep_b)


# Using context managers in dependencies with yield
"""
In Python, you can create Context Managers by creating a class with two methods: __enter__() and __exit__()
"""
class MySuperContextManager:
    def __init__(self):
        self.db = DBSession()

    def __enter__(self):
        return self.db

    def __exit__(self, exc_type, exc_value, traceback):
        self.db.close()


async def get_db():
    with MySuperContextManager() as db:
        yield db
import time
from datetime import datetime, time, timedelta
from typing import Optional, Dict, List, Set
from enum import Enum

from uuid import UUID

from fastapi import BackgroundTasks, Query, Path, Body, Header, status, Form, File, UploadFile
from fastapi.responses import HTMLResponse
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
    price: float = Field(...,  ge=0, le=1000, example=35.4)
    tax: Optional[float] = Field(default=0.1, example=3.2)
    tags: Set[str] = Field(set(), example=["blue", "green"])
    images: Optional[List[Image]] = Field(None, example=["http://my-image-url.com"])







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
    time.sleep(3)  # simulates heavy I/O
    with open("task_out.txt", mode="a") as f:
        content = f"{item} | {model_name} | {task_name} | {task_id} | {datetime.now()}\n"
        f.write(content)


@app.post("/task/run/{task_id}", status_code=status.HTTP_200_OK)
async def task_run(
    model_name: ModelName,
    background_tasks: BackgroundTasks,
    item: Item = Body(..., embed=True),
    user: User = Body(..., embed=True),
    importance: int = Body(..., ge=0, le=5, example=3),
    task_id: int = Path(..., description="The ID of the task to run", le=1000),
    task_name: str = Query(..., title="Query string", description="Query string for the task name", alias="task-name", max_length=50, regex="^.*$"),
    dry_run: Optional[bool] = False,
) -> Dict:
    """
    Async function that takes in a task and writes into a file
    by calling the background task `_task_run`
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
    start_datetime: Optional[datetime] = Body(None, example="2020-08-18T14:38:07.741Z"),
    end_datetime: Optional[datetime] = Body(None, example="2020-08-18T14:40:07.741Z"),
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
async def login_with_form_params(username: str = Form(...), password: str = Form(...)):
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
    file: bytes = File(...), fileb: UploadFile = File(...), token: str = Form(...), dummy_query_string: str = Query(None),
):
    return {
        "file_size": len(file),
        "token": token,
        "fileb_content_type": fileb.content_type,
    }
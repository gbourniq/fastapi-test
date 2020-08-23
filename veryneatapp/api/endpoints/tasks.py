from datetime import datetime
from enum import Enum
from time import sleep
from typing import Dict, Optional

from fastapi import APIRouter, BackgroundTasks, Body, Path, Query, status

from veryneatapp.api.schemas.item import Item
from veryneatapp.api.schemas.user import User

router = APIRouter()


class ModelName(str, Enum):
    """
    Enum which set a number of model names which
    can be seleted as query/path parameters
    """

    alexnet = "alexnet"
    resnet = "resnet"
    lenet = "lenet"


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


@router.post(
    "/run/{task_id}", status_code=status.HTTP_200_OK,
)
async def task_run(
    model_name: ModelName,
    background_tasks: BackgroundTasks,
    item: Item = Body(..., title="Item within request body", embed=True),
    user: User = Body(..., title="User within request body", embed=True),
    importance: int = Body(..., title="Int. within Req. Body", ge=0, example=3),
    task_id: int = Path(..., description="The ID of the task to run", le=1000),
    task_name: str = Query(..., alias="task-name", max_length=50, regex="^.*$"),
    dry_run: Optional[bool] = Query(default=False),
) -> Dict:
    """
    Async path operation that takes task params and writes into a file
    by calling the background task `_task_run`.
    Background tasks suitable for operations that need to happen after a request.
    (when the client doesn't have to be waiting for the operation to complete before receiving the response.)
    Eg. Email notifications, data processing, etc. (For longer processes, use celery.)

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

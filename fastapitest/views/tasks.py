import time
from datetime import datetime

from fastapi import BackgroundTasks

from fastapitest import app


def _task_run(name: str, task_id: int = None) -> None:
    """Private function to simulate an heavy I/O operation

    Args:
        name (str): name of the task
        task_id (int, optional): id of the task
        
    Output:
        append data to log file
    """
    time.sleep(3)  # simulates heavy I/O
    with open("task_out.txt", mode="a") as f:
        content = f"{name} | {task_id} | {datetime.now()}\n"
        f.write(content)


@app.post("/task/run/{name}/{task_id}")
async def task_run(
    name: str, task_id: int, background_tasks: BackgroundTasks
) -> dict:
    """Async function that takes in a task and writes into a file

    Args:
        name (str): name of the task
        task_id (int): id of the task
        background_tasks (BackgroundTasks): [description]
        
    Returns:
        None: HTTP response to the user
    """

    background_tasks.add_task(_task_run, name, task_id)
    return {"message": f"Task {name} ID {task_id} is being run..."}

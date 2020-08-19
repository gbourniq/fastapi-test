from fastapi import Depends, FastAPI, Header, HTTPException, Request
import time
from .routers import items, users

app = FastAPI()

# Middleware to add a response header such as
# x-process-time: 0.0004627704620361328 to every requests
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response

async def get_token_header(x_token: str = Header(default="fake-super-secret-token")):
    if x_token != "fake-super-secret-token":
        raise HTTPException(status_code=400, detail="X-Token header invalid")


app.include_router(users.router)
app.include_router(
    items.router,
    prefix="/items",
    tags=["items"],
    dependencies=[Depends(get_token_header)],
    responses={404: {"description": "Not found"}},
)
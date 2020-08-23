from fastapi import APIRouter, Depends, Header, HTTPException

from veryneatapp.api.endpoints import (
    basics,
    cust_exceptions,
    files,
    items,
    security,
    tasks,
    users,
)


async def get_token_header(
    x_token: str = Header(default="fake-super-secret-token"),
):
    if x_token != "fake-super-secret-token":
        raise HTTPException(status_code=400, detail="X-Token header invalid")


api_router = APIRouter()
api_router.include_router(
    basics.router,
    prefix="/basics",
    tags=["basics"],
    dependencies=[Depends(get_token_header)],
)
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(items.router, prefix="/items", tags=["items"])
api_router.include_router(cust_exceptions.router, tags=["exceptions"])
api_router.include_router(tasks.router, prefix="/tasks", tags=["tasks"])
api_router.include_router(files.router, prefix="/files", tags=["files"])
api_router.include_router(security.router, tags=["security"])

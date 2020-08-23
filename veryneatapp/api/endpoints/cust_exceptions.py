from fastapi import APIRouter
from veryneatapp.api.custom_exceptions import UnicornException

router = APIRouter()


@router.get("/custom-exception-handler-unicorns/{name}")
async def read_unicorn(name: str):
    """
    Pass `yolo` as the path parameter to trigger the custom exception
    """
    if name == "yolo":
        raise UnicornException(name=name)
    return {"unicorn_name": name}

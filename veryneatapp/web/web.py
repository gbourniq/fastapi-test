from fastapi import APIRouter

from veryneatapp.web.endpoints import home

web_router = APIRouter()

web_router.include_router(home.router)

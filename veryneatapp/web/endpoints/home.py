from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter()

templates = Jinja2Templates(directory="templates")


@router.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """
    GET route which returns HTML template,
    run curl http://0.0.0.0:5700/
    """
    return templates.TemplateResponse(
        "index.html", context={"request": request}
    )

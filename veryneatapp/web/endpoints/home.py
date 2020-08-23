from pathlib import Path

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter()

TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "templates"

templates = Jinja2Templates(directory=TEMPLATES_DIR)


@router.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """
    GET route which returns HTML template,
    run curl http://0.0.0.0:5700/
    """
    return templates.TemplateResponse(
        "index.html", context={"request": request}
    )

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from fastapitest.views import main, tasks

app = FastAPI()

app.mount(
    "/static", StaticFiles(directory="./fastapitest/static"), name="static"
)
templates = Jinja2Templates(directory="./fastapitest/templates")

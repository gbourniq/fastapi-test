from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI()

app.mount(
    "/static", StaticFiles(directory="./fastapitest/static"), name="static"
)
templates = Jinja2Templates(directory="./fastapitest/templates")

from fastapitest.views import main, tasks, security

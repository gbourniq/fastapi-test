from fastapi import Depends, FastAPI, Header, HTTPException, Request
import time
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from fastapitest.routers import basics, advanced, security

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


app = FastAPI()

### MIDDLEWARE ###
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


### TEMPLATES ###
@app.get("/")
async def index(request: Request):
    """
    GET route which returns HTML template,
    run curl http://0.0.0.0:5700/
    """
    return templates.TemplateResponse(
        "index.html", context={"request": request}
    )


### ROUTERS ###
app.include_router(basics.router)
app.include_router(advanced.router)
app.include_router(security.router)
# app.include_router(
#     items.router,
#     prefix="/items",
#     tags=["items"],
#     dependencies=[Depends(get_token_header)],
#     responses={404: {"description": "Not found"}},
# )


### CUSTOM EXCEPTION HANDLERS ###
class UnicornException(Exception):
    def __init__(self, name: str):
        self.name = name


@app.exception_handler(UnicornException)
async def unicorn_exception_handler(request: Request, exc: UnicornException):
    return JSONResponse(
        status_code=418,
        content={
            "message": f"Oops! {exc.name} did something. There goes a rainbow..."
        },
    )


@app.get("/custom-exception-handler-unicorns/{name}")
async def read_unicorn(name: str):
    """
    Pass `yolo` as the path parameter to trigger the exception
    """
    if name == "yolo":
        raise UnicornException(name=name)
    return {"unicorn_name": name}



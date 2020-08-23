import time

import graphene
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from starlette.graphql import GraphQLApp
from starlette.middleware.cors import CORSMiddleware

from veryneatapp.api import api_router
from veryneatapp.api.custom_exceptions import UnicornException
from veryneatapp.core.config import settings
from veryneatapp.web.web import web_router

# Initialise FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.PROJECT_DESCRIPTION,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=f"{settings.API_V1_DOCS}",
    redoc_url=None,
)

# Add templates and mount static files
# app.mount("/static", StaticFiles(directory="static"), name="static")

# Add middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """
    Middleware to add the `x-process-time` response header
    to every requests. Eg: x-process-time: 0.0004627704620361328 
    """
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


# Load custom exception handlers
@app.exception_handler(UnicornException)
async def unicorn_exception_handler(request: Request, exc: UnicornException):
    return JSONResponse(
        status_code=418,
        content={
            "message": f"Oops! {exc.name} did something. There goes a rainbow..."
        },
    )


# Set all CORS enabled origins
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Load all routes
app.include_router(api_router, prefix=settings.API_V1_STR)
app.include_router(web_router, tags=["frontend"])


# Add GraphQL
class SampleQuery4GraphQL(graphene.ObjectType):
    """
    GraphQL web user interface at /graphql, run:
    {
    hello(name: "FastAPI")
    }
    To learn how to use GraphQL: https://www.starlette.io/graphql/
    """

    hello = graphene.String(name=graphene.String(default_value="stranger"))

    def resolve_hello(self, info, name):
        return "Hello " + name


app.add_route(
    "/graphql", GraphQLApp(schema=graphene.Schema(query=SampleQuery4GraphQL))
)

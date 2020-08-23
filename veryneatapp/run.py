import uvicorn

from veryneatapp.core.config import settings

if __name__ == "__main__":
    uvicorn.run(
        "veryneatapp.main:app",
        host=settings.WEBSERVER_HOST,
        port=settings.WEBSERVER_PORT,
        reload=settings.RELOAD,
        debug=settings.DEBUG,
        workers=settings.WORKERS_COUNT,
    )

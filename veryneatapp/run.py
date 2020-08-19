import uvicorn

from config import WEBSERVER_PORT, RELOAD, DEBUG, WORKERS_COUNT

if __name__ == "__main__":
    uvicorn.run(
        "veryneatapp.main:app",
        host="0.0.0.0",
        port=WEBSERVER_PORT,
        reload=RELOAD,
        debug=DEBUG,
        workers=WORKERS_COUNT,
    )

import uvicorn

from config import WEBSERVER_PORT

if __name__ == "__main__":
    uvicorn.run(
        "fastapitest:app",
        host="0.0.0.0",
        port=(WEBSERVER_PORT),
        reload=False,
        debug=False,
        workers=30,
    )

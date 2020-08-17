from fastapi import Request

from fastapitest import app, templates


@app.get("/")
async def index(request: Request):
    """
    GET route which returns HTML template,
    run curl http://0.0.0.0:5700/
    """
    return templates.TemplateResponse(
        "index.html", context={"request": request}
    )


@app.get("/tutorial")
async def tutorial():
    """This is a simple GET route, to use this
    run curl http://0.0.0.0:5700/tutorial
    """
    return {"message": {"this is another route"}}

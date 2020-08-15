from fastapi import Request

from fastapitest import app, templates


@app.get("/")
async def index(request: Request):
    return templates.TemplateResponse(
        "index.html", context={"request": request}
    )


@app.get("/tutorial")
async def tutorial():
    """This is a tutorial function, to use this
    run curl http://0.0.0.0:5700/tutorial

    Returns:
        None: returns http response
    """
    return {"message": {"this is another route"}}

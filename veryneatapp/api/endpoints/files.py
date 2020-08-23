from fastapi import APIRouter, status, Path, Query, File, Form, UploadFile
from fastapi.responses import HTMLResponse
from typing import Dict, List, Optional, Union, Set

router = APIRouter()

# more info: https://fastapi.tiangolo.com/tutorial/request-files/


@router.post("/upload-files/", status_code=status.HTTP_201_CREATED)
async def upload_files(files: List[UploadFile] = File(...)):
    """
    Upload files and save file to server filesystem
    """
    for myfile in files:
        binary_file = myfile.file._file.read() # read file into memory
        with open(myfile.filename.split("¦")[-1], "w+b") as f:
            f.write(binary_file)

    return {"files": [_file.__dict__ for _file in files]}


@router.post("/upload-files-and-form-data/", status_code=status.HTTP_202_ACCEPTED)
async def upload_files_and_form_data(
    file_A: bytes = File(...),
    file_B: UploadFile = File(...),
    token: str = Form(...),
    dummy_query_string: str = Query(None),
):
    return {
        "file_size": len(file_A),
        "token": token,
        "fileb_content_type": file_B.content_type,
    }




# Upload file via a web page
# This route retrieve 2 form actions: /files/ and /uploadfiles/
# @router.get("/upload/", status_code=status.HTTP_201_CREATED)
# async def main():
#     content = """
# <body>
# <form action="/files/" enctype="multipart/form-data" method="post">
# <input name="files" type="file" multiple>
# <input type="submit">
# </form>
# <form action="/uploadfiles/" enctype="multipart/form-data" method="post">
# <input name="files" type="file" multiple>
# <input type="submit">
# </form>
# </body>
#     """
#     return HTMLResponse(content=content)
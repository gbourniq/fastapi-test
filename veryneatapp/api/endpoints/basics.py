from fastapi import APIRouter, Cookie, status, Path, Body, Depends
from typing import Dict, List, Optional, Union, Set
from datetime import datetime, time, timedelta
from uuid import UUID
from veryneatapp.api.dependencies.core_dependencies import CommonQueryParams, KeyTokenAuth, query_or_cookie_extractor

router = APIRouter()

# Simple GET and POST routes
@router.get("/tutorial")
async def tutorial():
    """This is a simple GET route, to use this
    run curl http://0.0.0.0:5700/tutorial
    """
    return {"message": {"this is another route"}}


@router.post("/index-weights/")
async def create_index_weights(weights: Dict[int, float]):
    """
    Request body to accept any dict as long as it has int keys with float values
    The request body sent by the client is expected to be in the form of:
        {"129385": 1.45}
    """
    return weights


@router.get("/cookie-example/")
async def read_items(ads_id: Optional[str] = Cookie(None)):
    """Cookie example
    declare the cookie parameters using the same structure as with Path and Query.
    The first value is the default value, you can pass all the extra validation or annotation parameters
    """
    return {"ads_id": ads_id}


@router.get("/deprecated-path/", deprecated=True)
async def read_elements():
    """
    Sample deprecated path
    """
    return [{"item_id": "Foo"}]


@router.put("/advanced-datatypes/{item_id}", status_code=status.HTTP_200_OK)
async def advanced_datatypes(
    item_id: UUID = Path(..., example="123e4567-e89b-12d3-a456-426614174000"),
    start_datetime: Optional[datetime] = Body(
        None, example="2020-08-18T14:38:07.741Z"
    ),
    end_datetime: Optional[datetime] = Body(
        None, example="2020-08-18T14:40:07.741Z"
    ),
    repeat_at: Optional[time] = Body(None, example="14:23:55.003"),
    process_after: Optional[timedelta] = Body(None, example="11.03"),
):
    """
    Route using the advanced data types: UUID, datetime, time, timedelta
    """
    start_process = start_datetime + process_after
    duration = end_datetime - start_process
    return {
        "item_id": item_id,
        "start_datetime": start_datetime,
        "end_datetime": end_datetime,
        "repeat_at": repeat_at,
        "process_after": process_after,
        "start_process": start_process,
        "duration": duration,
    }

# DEPENDENCIES
"""
"Dependency Injection" means, in programming, that there is a way for your code
(in this case, your path operation functions) to declare things that
it requires to work and use: "dependencies". This minimizes code repetition!

This is very useful when you need to:
- Have shared logic (the same code logic again and again).
- Share database connections.
- Enforce security, authentication, role requirements, etc.
- And many other things...

The simplicity of the dependency injection system makes FastAPI compatible with:
- all the relational databases
- NoSQL databases
- external packages
- external APIs
- authentication and authorization systems
- API usage monitoring systems
- response data injection systems
- etc.

All these dependencies, while declaring their requirements, 
also add parameters, validations, etc. to your path operations.
"""

# In the case below, we abstract the Query/Path/Body parameters 
# by definining them in a class dependency CommonQueryParams
@router.get("/simple-dependency/", tags=["dependencies examples"])
async def read_items(commons: CommonQueryParams = Depends(CommonQueryParams)):
    """
    FastAPI calls the CommonQueryParams class. This creates an "instance" of that class
    and the instance will be passed as the parameter commons to your function.

    Whenever a new request arrives, FastAPI will take care of:
    - Calling your dependency ("dependable") function with the correct parameters.
    - Get the result from your function.
    - Assign that result to the parameter in your path operation function.
    - This way you write shared code once and FastAPI takes care of calling it for your path operations.
    """
    return commons


# Dependency use case: If the user didn't provide any query q,
# we use the last query used, which we saved to a cookie before.
@router.get("/query-or-cookie/", tags=["dependencies examples"])
async def read_query_or_cookie_extractor(
    query_or_default: str = Depends(query_or_cookie_extractor),
):
    return {"q_or_cookie": query_or_default}


# For dependencies that dont return any values - using `dependencies=`
@router.get(
    "/no-returned-values-from-depencies/",
    dependencies=[Depends(KeyTokenAuth.verify_token), Depends(KeyTokenAuth.verify_key)],
    tags=["dependencies examples"]
)
async def read_items():
    return [{"item": "Foo"}, {"item": "Bar"}]


# Dependencies that do some extra steps after finishing (based on yield)
async def get_db():
    db = DBSession()  # executed before sending a response
    try:
        yield db  # what is injected into the path operations and other dependencies
    finally:
        db.close()  #  executed after the response has been delivered

"""
It might be tempting to raise an HTTPException or similar in the exit code, 
AFTER the yield. But it won't work. because the request is already sent. (Can do it before only._
If you have some code that you know could raise an exception, 
do the most normal/"Pythonic" thing and add a try block in that section of the code.
"""
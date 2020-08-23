from typing import Optional

from fastapi import Cookie, Depends, Header

from veryneatapp.api.schemas.user import UserCreate, UserInDB


class CommonQueryParams:
    """First dependency (must be callable)
    that expects 3 optional query parameters

    Args:
        q (str, optional). Defaults to None.
        skip (int, optional). Defaults to 0.
        limit (int, optional). Defaults to 100.

    Returns:
        (dict). dict containing those values
    """

    def __init__(
        self, q: Optional[str] = None, skip: int = 0, limit: int = 100
    ):
        self.q = q
        self.skip = skip
        self.limit = limit


"""
If the user didn't provide any query q,
we use the last query used, which we saved to a cookie before.
"""


def query_extractor(q: Optional[str] = None):
    return q


def query_or_cookie_extractor(
    q: str = Depends(query_extractor),
    last_query: Optional[str] = Cookie(default="last-default-dummy-query"),
):
    if not q:
        return last_query
    return q


class KeyTokenAuth:
    @staticmethod
    # For dependencies that dont return any values - call them with `dependencies=`
    async def verify_token(
        x_token: str = Header(default="fake-super-secret-token"),
    ):
        if x_token != "fake-super-secret-token":
            raise HTTPException(
                status_code=400, detail="X-Token header invalid"
            )
        return x_token  # won't be used because if called with dependencies=[Depends(KeyTokenAuth.verify_token)]

    @staticmethod
    async def verify_key(x_key: str = Header(default="fake-super-secret-key")):
        if x_key != "fake-super-secret-key":
            raise HTTPException(status_code=400, detail="X-Key header invalid")
        return x_key  # won't be used because if called with dependencies=[Depends(KeyTokenAuth.verify_key)]


# Dependencies that do some extra steps after finishing (based on yield)
class DatabaseConnect:
    @staticmethod
    async def get_db():
        db = DBSession()  # executed before sending a response
        try:
            yield db  # what is injected into the path operations and other dependencies
        finally:
            db.close()  #  executed after the response has been delivered


class DummyUserManagementExample:
    @staticmethod
    def fake_password_hasher(raw_password: str):
        return "supersecret" + raw_password

    @staticmethod
    def fake_save_user(user_in: UserCreate):
        hashed_password = DummyUserManagementExample.fake_password_hasher(
            user_in.password
        )
        user_in_db = UserInDB(**user_in.dict(), hashed_password=hashed_password)
        print("User saved! ..not really")
        return user_in_db

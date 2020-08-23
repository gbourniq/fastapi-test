from os import getenv
from typing import List, Union

from pydantic import AnyHttpUrl, BaseSettings, validator


class Settings(BaseSettings):

    PROJECT_NAME: str = getenv("PROJECT_NAME", "Default Project Name")
    PROJECT_DESCRIPTION: str = getenv(
        "PROJECT_DESCRIPTION", "Default Project Description"
    )
    VERSION: str = getenv("VERSION", "0.1.0")
    API_V1_STR: str = "/api/v1"
    WEBSERVER_HOST: str = getenv("WEBSERVER_HOST", "0.0.0.0")
    WEBSERVER_PORT: int = int(getenv("WEBSERVER_PORT", 5700))

    RELOAD: bool = getenv("RELOAD", True)
    DEBUG: bool = getenv("DEBUG", True)
    WORKERS_COUNT: int = int(getenv("WORKERS_COUNT", 1))

    # BACKEND_CORS_ORIGINS is a JSON-formatted list of origins
    # e.g: '["http://localhost", "http://localhost:4200", "http://localhost:3000", \
    # "http://localhost:8080", "http://local.dockertoolbox.tiangolo.com"]'
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []

    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(
        cls, v: Union[str, List[str]]
    ) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    class Config:
        case_sensitive = True


settings = Settings()

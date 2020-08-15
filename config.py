"""
This file collects environment variables across the repo and store them into global
variables. This allows to easily update the code base if in the future a variable
is renamed or removed.
"""

import os

WEBSERVER_PORT = os.getenv("WEBSERVER_PORT", 5700)
RELOAD = os.getenv("RELOAD", True)
DEBUG = os.getenv("DEBUG", True)
WORKERS_COUNT = os.getenv("WORKERS_COUNT", 1)

ENV_VARS = [
    "WEBSERVER_PORT",
    "RELOAD",
    "DEBUG",
    "WORKERS_COUNT",
]

for ENV_VAR in ENV_VARS:
    if not locals().get(ENV_VAR):
        raise EnvironmentError(
            f"The {ENV_VAR} environment variable has not been "
            "set. Please set this environment variable."
        )

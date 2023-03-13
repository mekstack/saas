# pylint: disable=too-few-public-methods
import os


class Config:
    JWT_MAX_AGE_SECONDS = 600

    try:
        SECRET_KEY = os.environ["SECRET_KEY"]
        JWT_SECRET_KEY = os.environ["JWT_SECRET_KEY"]
        KEYCLOAK_CLIENT_ID = os.environ["KEYCLOAK_CLIENT_ID"]
        KEYCLOAK_CLIENT_SECRET = os.environ["KEYCLOAK_CLIENT_SECRET"]
        KEYCLOAK_METADATA_URL = os.environ["KEYCLOAK_METADATA_URL"]
    except KeyError as key:
        raise RuntimeError(f"Flask configuration failed. {key} is unset") from key

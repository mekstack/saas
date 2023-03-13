import datetime
import logging

import jwt
from authlib.integrations.flask_client import OAuth
from flask import Flask, make_response, redirect, url_for

from auth import util

app = Flask("auth")
util.setup_logging()
log = logging.getLogger("auth")

app.config.from_object("config.Config")

oauth = OAuth(app)

oauth.register(
    name="keycloak",
    client_id=app.config["KEYCLOAK_CLIENT_ID"],
    client_secret=app.config["KEYCLOAK_CLIENT_SECRET"],
    server_metadata_url=app.config["KEYCLOAK_METADATA_URL"],
    client_kwargs={"scope": "openid email profile"},
)
log.info("Registered OAuth provider")

keycloak = oauth.create_client("keycloak")
assert keycloak is not None


@app.route("/login")
def login():
    url = url_for("redirect_uri", _external=True)
    return keycloak.authorize_redirect(url)


@app.route("/redirect_uri")
def redirect_uri():
    def create_jwt(email):
        return jwt.encode(
            {
                "email": email.split("@")[0],
                "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=10),
            },
            app.config["JWT_SECRET_KEY"],
        )

    token = keycloak.authorize_access_token()
    email = token["userinfo"]["email"]

    log.info("Logged in user %s", email)

    response = make_response(redirect("/"))
    response.set_cookie(
        "accessToken",
        create_jwt(email),
        httponly=True,
        secure=True,
        samesite="Lax",
        max_age=app.config["JWT_MAX_AGE_SECONDS"],
    )
    return response

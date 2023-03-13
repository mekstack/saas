# pylint: disable=too-few-public-methods
import jwt
import pytest
from werkzeug.http import parse_cookie

from auth.app import app, keycloak


@pytest.fixture(autouse=True)
def mock_oauth_client(monkeypatch):
    def authorize_access_token():
        userinfo = {"email": "test@gmail.com"}
        token = {
            "access_token": "foo",
            "id_token": jwt.encode(userinfo, "secret"),
            "userinfo": userinfo,
        }
        return token

    monkeypatch.setattr(keycloak, "authorize_access_token", authorize_access_token)


def test_login_basic():
    response = app.test_client().get("/redirect_uri")

    assert response.status_code == 302


def test_login_logging(caplog):
    app.test_client().get("/redirect_uri")

    assert "Logged in user test@gmail.com" in caplog.text


def test_login_jwt():
    response = app.test_client().get("/redirect_uri")
    cookies = response.headers.getlist("Set-Cookie")
    jwt_cookie = next((cookie for cookie in cookies if "accessToken" in cookie), None)

    assert jwt_cookie is not None

    jwt_cookie_attrs = parse_cookie(jwt_cookie)

    assert "Secure" in jwt_cookie_attrs
    assert "HttpOnly" in jwt_cookie_attrs
    assert jwt_cookie_attrs["SameSite"] == "Lax"
    assert jwt_cookie_attrs["Max-Age"] == str(app.config["JWT_MAX_AGE_SECONDS"])

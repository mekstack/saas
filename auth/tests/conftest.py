import os

import pytest

os.environ["SECRET_KEY"] = "secret"
os.environ["JWT_SECRET_KEY"] = "secret"
os.environ["KEYCLOAK_CLIENT_ID"] = "secret"
os.environ["KEYCLOAK_CLIENT_SECRET"] = "secret"
os.environ["KEYCLOAK_METADATA_URL"] = "secret"

@pytest.fixture(autouse=True)
def no_requests(monkeypatch):
    """Remove requests.sessions.Session.request for all tests."""
    monkeypatch.delattr("requests.sessions.Session.request")

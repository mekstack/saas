# SaaS

Service as a Service services

## Installation

Python dependencies are tracked with poetry. To install dependencies run

    poetry install
    poetry update

## Microservices

### Auth

Provides an HTTP endpoint `/login/<provider>` that authorizes user via OAuth
provider and returns a signed JWT token.

#### Configuration

Configuration is performed by setting following variables.

-   **FLASK_OAUTH_PROVIDERS**: list of provider names.

    Example: `FLASK_OAUTH_PROVIDERS = ["google", "keycloak"]`

    Each OAuth provider is configured with env variables formatted as
    **`FLASK_{provider_name}_{option}`**.
    **`provider_name` must be uppercase**.
    Required `option`s are `CLIENT_ID`, `CLIENT_SECRET` and `METADATA_URL`.
    Example: ` FLASK_GOOGLE_CLIENT_ID = client_id`

-   **FLASK_SECRET_KEY**: string that sets app.secret_key

-   **FLASK_JWT_SECRET_KEY**: string for JWT signing

Example configuration can be seen in .flaskenv file.

#### Run tests

    cd auth
    source (poetry env info --path)/bin/activate.fish
    pytest

## Development

To init a new service do

    poetry new <service name>

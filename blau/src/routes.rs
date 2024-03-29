use std::borrow::Cow;

use actix_session::Session;
use actix_web::{
    error::{ErrorForbidden as Forbidden, ErrorInternalServerError as ServerError},
    get, web, HttpRequest, HttpResponse,
};

use openidconnect::reqwest::async_http_client;
use openidconnect::{
    core::{CoreAuthenticationFlow, CoreClient},
    AuthorizationCode, CsrfToken, Nonce, RedirectUrl, Scope, TokenResponse,
};

use crate::{jwt::JwtEncoder, util::Util};

#[derive(serde::Deserialize)]
pub struct LoginPayload {
    redirect_back_url: Option<String>,
}

#[get("/login")]
async fn login(
    req: HttpRequest,
    params: web::Query<LoginPayload>,
    client: web::Data<CoreClient>,
    util: web::Data<Util>,
    session: Session,
) -> Result<HttpResponse, actix_web::Error> {
    let redirect_url = RedirectUrl::from_url(req.url_for_static("redirect_uri")?);

    let (authorize_url, csrf_state, nonce) = client
        .authorize_url(
            CoreAuthenticationFlow::AuthorizationCode,
            CsrfToken::new_random,
            Nonce::new_random,
        )
        .set_redirect_uri(Cow::Owned(redirect_url))
        .add_scope(Scope::new("openid email profile".to_string()))
        .url();

    session.insert("csrf_state", csrf_state.clone())?;
    session.insert("nonce", nonce.clone())?;

    session.insert(
        "redirect_back_url",
        util.get_redirect_back_url(params.redirect_back_url.clone())?,
    )?;

    Ok(HttpResponse::TemporaryRedirect()
        .append_header(("Location", authorize_url.to_string()))
        .finish())
}

#[derive(serde::Deserialize)]
pub struct RedirectUriPayload {
    code: String,
    state: String,
}

#[derive(serde::Serialize)]
pub struct JWTResponse {
    access_token: String,
}

#[get("/redirect_uri")]
async fn redirect_uri(
    req: HttpRequest,
    params: web::Query<RedirectUriPayload>,
    jwt: web::Data<JwtEncoder>,
    client: web::Data<CoreClient>,
    util: web::Data<Util>,
    session: Session,
) -> Result<HttpResponse, actix_web::Error> {
    if let Some(stored_state) = session.get::<String>("csrf_state")? {
        if stored_state != params.state {
            Err(Forbidden("Invalid CSRF state"))?
        }
    } else {
        Err(Forbidden("Missing CSRF state"))?
    }

    let code = AuthorizationCode::new(params.code.clone());
    let redirect_url = RedirectUrl::from_url(req.url_for_static("redirect_uri")?);
    let redirect_back_url =
        util.get_redirect_back_url(session.get::<String>("redirect_back_url")?)?;

    let token_response = client
        .exchange_code(code)
        .set_redirect_uri(Cow::Owned(redirect_url))
        .request_async(async_http_client)
        .await
        .map_err(|e| ServerError(format!("Token exchange failed: {}", e)))?;

    let id_token = token_response
        .id_token()
        .ok_or(ServerError("OpenID token not found in token response"))?;

    let nonce: Nonce = session
        .get("nonce")?
        .ok_or(Forbidden("Nonce not found in session"))?;

    let claims = id_token
        .claims(&client.id_token_verifier(), &nonce)
        .map_err(|e| Forbidden(format!("Failed to verify OpenID token claims: {}", e)))?;

    let email = claims
        .email()
        .ok_or(Forbidden("Email not found in OpenID token claims"))?;

    let username = email
        .splitn(2, '@')
        .next()
        .ok_or(ServerError("Failed to extract username from email"))?
        .to_string();

    log::info!("User '{}' logged in successfully", username);

    let access_token = jwt
        .encode(username)
        .map_err(|e| ServerError(format!("Failed to encode JWT: {}", e)))?;

    Ok(HttpResponse::TemporaryRedirect()
        .append_header((
            "Location",
            format!("{}#access_token={}", redirect_back_url, access_token),
        ))
        .finish())
}

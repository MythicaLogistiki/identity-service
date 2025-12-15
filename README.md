# identity-service

OIDC/OAuth2 Identity Provider for the Phase Zero SaaS platform.

## Purpose

Acts as the central authentication service and JWT issuer. All other services validate tokens against this service's JWKS endpoint.

## Features

- OIDC Discovery (`/.well-known/openid-configuration`)
- JWKS endpoint for token verification
- OAuth2 token endpoint (client_credentials, password, refresh_token grants)
- User registration and authentication
- Multi-tenant JWT claims (`tenant_id`, `role`)

## Stack

- Python 3.11
- FastAPI
- SQLAlchemy (async) + PostgreSQL
- Deployed on GCP Cloud Run

## Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /.well-known/openid-configuration` | OIDC discovery |
| `GET /.well-known/jwks.json` | Public keys |
| `POST /oauth2/token` | Token endpoint |
| `POST /users` | User registration |
| `POST /auth/login` | User login |

## Test locally

```
  cd identity-service
  python3.11 -m venv .venv && source .venv/bin/activate
  pip install -r requirements.txt
  uvicorn app.main:app --reload
```

Admin user: `admin@example.com`
Admin password: `admin123`


Standard user: `auser@example.com`
Standard password: `user123`




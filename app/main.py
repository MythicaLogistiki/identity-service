"""Identity Service - OIDC Provider for Phase Zero SaaS."""

import os
from datetime import datetime, timezone, timedelta
from uuid import UUID

from fastapi import FastAPI, HTTPException, status, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from jose import jwt

from app.models import TokenResponse, OIDCConfig, Role

# Config
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-secret-change-in-production")
ALGORITHM = "HS256"
TOKEN_EXPIRE_MINUTES = int(os.getenv("TOKEN_EXPIRE_MINUTES", "60"))
ISSUER = os.getenv("ISSUER", "http://localhost:8000")

# Mock user store (replace with DB in production)
MOCK_USERS = {
    "admin@example.com": {
        "password": "admin123",
        "tenant_id": "550e8400-e29b-41d4-a716-446655440000",
        "role": Role.ADMIN,
    },
    "user@example.com": {
        "password": "user123",
        "tenant_id": "550e8400-e29b-41d4-a716-446655440000",
        "role": Role.STANDARD,
    },
    # Platform admin - internal Numbersence staff
    "platform@numbersence.com": {
        "password": "platform123",
        "tenant_id": "00000000-0000-0000-0000-000000000000",  # Platform tenant
        "role": Role.PLATFORM_ADMIN,
    },
    # Support agent - customer support staff
    "support@numbersence.com": {
        "password": "support123",
        "tenant_id": "00000000-0000-0000-0000-000000000000",  # Platform tenant
        "role": Role.SUPPORT_AGENT,
    },
}

app = FastAPI(
    title="Identity Service",
    version="0.1.0",
    description="OIDC/OAuth2 Identity Provider for Phase Zero SaaS",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.get("/.well-known/openid-configuration", response_model=OIDCConfig)
async def openid_configuration():
    """OIDC Discovery endpoint."""
    return OIDCConfig(
        issuer=ISSUER,
        token_endpoint=f"{ISSUER}/token",
        jwks_uri=f"{ISSUER}/.well-known/jwks.json",
        response_types_supported=["token"],
        subject_types_supported=["public"],
        id_token_signing_alg_values_supported=[ALGORITHM],
        scopes_supported=["openid", "profile", "email"],
        claims_supported=["sub", "tenant_id", "role", "iat", "exp", "iss"],
    )


@app.get("/.well-known/jwks.json")
async def jwks():
    """JWKS endpoint (placeholder for symmetric key)."""
    return JSONResponse(
        content={"keys": []},
        headers={"Cache-Control": "public, max-age=3600"},
    )


@app.post("/token", response_model=TokenResponse)
async def token(
    username: str = Form(...),
    password: str = Form(...),
):
    """
    OAuth2 token endpoint.
    Accepts username/password, returns JWT with tenant_id and role.
    """
    user = MOCK_USERS.get(username)
    if not user or user["password"] != password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    now = datetime.now(timezone.utc)
    expire = now + timedelta(minutes=TOKEN_EXPIRE_MINUTES)

    payload = {
        "sub": username,
        "tenant_id": user["tenant_id"],
        "role": user["role"].value,
        "iat": int(now.timestamp()),
        "exp": int(expire.timestamp()),
        "iss": ISSUER,
    }

    access_token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

    return TokenResponse(
        access_token=access_token,
        expires_in=TOKEN_EXPIRE_MINUTES * 60,
    )

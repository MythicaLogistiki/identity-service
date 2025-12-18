"""Pydantic models for identity-service."""

from uuid import UUID
from enum import Enum
from pydantic import BaseModel, EmailStr, Field


class Role(str, Enum):
    STANDARD = "standard"
    ADMIN = "admin"
    PLATFORM_ADMIN = "platform_admin"
    SUPPORT_AGENT = "support_agent"


class TokenRequest(BaseModel):
    """OAuth2 password grant request."""
    username: EmailStr
    password: str = Field(min_length=1)


class TokenResponse(BaseModel):
    """OAuth2 token response."""
    access_token: str
    token_type: str = "Bearer"
    expires_in: int


class TokenPayload(BaseModel):
    """JWT payload claims."""
    sub: str
    tenant_id: UUID
    role: Role
    exp: int
    iat: int
    iss: str


class OIDCConfig(BaseModel):
    """OpenID Connect discovery document."""
    issuer: str
    token_endpoint: str
    jwks_uri: str
    response_types_supported: list[str]
    subject_types_supported: list[str]
    id_token_signing_alg_values_supported: list[str]
    scopes_supported: list[str]
    claims_supported: list[str]

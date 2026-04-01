"""
auth/validator.py
-----------------
Core validation logic.

Flow:
  1. Decode header (không verify) → lấy kid + alg
  2. Tìm provider phù hợp dựa vào claim `iss` trong payload (unverified)
  3. Fetch public key từ JWKSCache của provider đó
  4. Verify đầy đủ: signature + iss + aud + exp + nbf
  5. Trả về TokenPayload đã validate
"""

from __future__ import annotations

import logging
from typing import Any

import jwt
from jwt.exceptions import (
    DecodeError,
    ExpiredSignatureError,
    InvalidAudienceError,
    InvalidIssuerError,
    InvalidTokenError,
    MissingRequiredClaimError,
)
from pydantic import BaseModel, Field

from auth.config import ProviderConfig
from auth.jwks import JWKSCache

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Token payload model
# ---------------------------------------------------------------------------

class TokenPayload(BaseModel):
    """Claims chuẩn của OIDC/OAuth2 token sau khi validate thành công."""

    # Standard claims
    sub: str                        # Subject (user identifier tại provider)
    iss: str                        # Issuer
    aud: str | list[str]            # Audience
    exp: int                        # Expiry (unix timestamp)
    iat: int | None = None          # Issued at
    nbf: int | None = None          # Not before

    # OIDC standard claims (optional, có thể không có trong access_token)
    email: str | None = None
    email_verified: bool | None = None
    name: str | None = None
    picture: str | None = None

    # Provider name (gán thêm sau khi validate, không có trong token)
    provider: str = Field(default="", exclude=True)

    # Toàn bộ raw claims — để caller tự lấy claim tùy ý
    raw_claims: dict[str, Any] = Field(default_factory=dict, exclude=True)

    model_config = {"extra": "ignore"}


# ---------------------------------------------------------------------------
# Provider registry
# ---------------------------------------------------------------------------

class ProviderRegistry:
    """
    Giữ danh sách providers và JWKS cache tương ứng.
    Index theo issuer string để lookup nhanh khi validate.
    """

    def __init__(self, providers: list[ProviderConfig]) -> None:
        if not providers:
            raise ValueError("ProviderRegistry requires at least one provider")

        self._providers: dict[str, ProviderConfig] = {}
        self._caches: dict[str, JWKSCache] = {}

        for p in providers:
            issuer = p.issuer_str
            if issuer in self._providers:
                raise ValueError(f"Duplicate issuer in provider config: {issuer}")
            self._providers[issuer] = p
            self._caches[issuer] = JWKSCache(p)
            logger.info("Registered auth provider '%s' (issuer: %s)", p.name, issuer)

    def find_by_issuer(self, issuer: str) -> tuple[ProviderConfig, JWKSCache] | None:
        issuer = issuer.rstrip("/")
        if issuer in self._providers:
            return self._providers[issuer], self._caches[issuer]
        return None

    @property
    def provider_names(self) -> list[str]:
        return [p.name for p in self._providers.values()]


# ---------------------------------------------------------------------------
# Validator
# ---------------------------------------------------------------------------

class ExternalTokenValidator:
    """
    Validate JWT token từ bất kỳ provider nào đã đăng ký.

    Usage:
        validator = ExternalTokenValidator(registry)
        payload = await validator.validate(token)
    """

    def __init__(self, registry: ProviderRegistry) -> None:
        self._registry = registry

    async def validate(self, token: str) -> TokenPayload:
        """
        Validate token và trả về TokenPayload.
        Raise TokenValidationError nếu token không hợp lệ.
        """
        # Bước 1: Decode header và unverified payload để biết iss + kid
        header, unverified_claims = _decode_unverified(token)

        kid = header.get("kid")
        alg = header.get("alg", "RS256")
        issuer = unverified_claims.get("iss", "").rstrip("/")

        if not issuer:
            raise TokenValidationError("Token missing 'iss' claim")

        # Bước 2: Tìm provider theo issuer
        result = self._registry.find_by_issuer(issuer)
        if result is None:
            raise TokenValidationError(
                f"Unknown issuer '{issuer}'. "
                f"Registered providers: {self._registry.provider_names}"
            )
        provider, jwks_cache = result

        # Bước 3: Kiểm tra algorithm có nằm trong whitelist của provider không
        if alg not in provider.algorithms:
            raise TokenValidationError(
                f"Algorithm '{alg}' not allowed for provider '{provider.name}'. "
                f"Allowed: {provider.algorithms}"
            )

        # Bước 4: Lấy public key
        if not kid:
            raise TokenValidationError(
                f"Token from provider '{provider.name}' missing 'kid' in header. "
                "Cannot select JWKS key."
            )

        try:
            public_key = await jwks_cache.get_key(kid)
        except KeyError as exc:
            raise TokenValidationError(str(exc)) from exc
        except Exception as exc:
            raise TokenValidationError(
                f"Failed to fetch JWKS for provider '{provider.name}': {exc}"
            ) from exc

        # Bước 5: Verify đầy đủ
        try:
            claims = jwt.decode(
                token,
                key=public_key,
                algorithms=provider.algorithms,
                audience=provider.effective_audience,
                issuer=provider.issuer_str,
                options={
                    "require": ["sub", "iss", "aud", "exp"],
                    "verify_exp": True,
                    "verify_nbf": True,
                    "verify_iss": True,
                    "verify_aud": True,
                    "verify_signature": True,
                },
            )
        except ExpiredSignatureError:
            raise TokenValidationError("Token has expired")
        except InvalidAudienceError:
            raise TokenValidationError(
                f"Token audience does not match expected '{provider.effective_audience}'"
            )
        except InvalidIssuerError:
            raise TokenValidationError(
                f"Token issuer does not match expected '{provider.issuer_str}'"
            )
        except MissingRequiredClaimError as exc:
            raise TokenValidationError(f"Token missing required claim: {exc}") from exc
        except DecodeError as exc:
            raise TokenValidationError(f"Token decode error: {exc}") from exc
        except InvalidTokenError as exc:
            raise TokenValidationError(f"Token invalid: {exc}") from exc

        payload = TokenPayload(**claims, raw_claims=claims)
        payload.provider = provider.name
        return payload


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _decode_unverified(token: str) -> tuple[dict[str, Any], dict[str, Any]]:
    """Decode header và payload mà không verify signature."""
    try:
        header = jwt.get_unverified_header(token)
        claims = jwt.decode(
            token,
            options={"verify_signature": False},
            algorithms=jwt.algorithms.get_default_algorithms().keys(),
        )
        return header, claims
    except DecodeError as exc:
        raise TokenValidationError(f"Malformed JWT: {exc}") from exc


# ---------------------------------------------------------------------------
# Custom exception
# ---------------------------------------------------------------------------

class TokenValidationError(Exception):
    """Raised khi token không pass validation."""
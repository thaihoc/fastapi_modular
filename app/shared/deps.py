from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi_cache.decorator import cache

import httpx
import logging

logger = logging.getLogger(__name__)

from app.db.session import SessionLocal

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def get_http_client():
    async with httpx.AsyncClient(timeout=5.0) as client:
        yield client


@cache(expire=300)
async def get_auth_jwks(
    client: httpx.AsyncClient = Depends(get_http_client)
):
    from app.core.config import settings

    if not settings.auth_jwks:
        return None

    try:
        response = await client.get(settings.auth_jwks)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.error(f"Failed to fetch JWKS: {e}")
        return None


security = HTTPBearer(auto_error=False)


def get_token(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    if not credentials:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return credentials.credentials


def validate_token(
    token: str = Depends(get_token),
    jwks: dict = Depends(get_auth_jwks)
):
    from authlib.jose import jwt
    from app.core.config import settings

    if not jwks:
        raise HTTPException(status_code=401, detail="JWKS not found")

    try:
        claims = jwt.decode(token, jwks)
        claims.validate()

        if settings.auth_issuer:
            claims.validate_iss(settings.auth_issuer)

        if settings.auth_audience:
            claims.validate_aud(settings.auth_audience)

        return claims

    except HTTPException:
        raise

    except Exception as e:
        logger.error(f"JWT error: {e}")
        raise HTTPException(status_code=401, detail="Invalid token")
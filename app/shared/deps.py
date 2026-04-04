from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi_cache.decorator import cache

import httpx
import logging
from authlib.jose import jwt
from app.core.config import settings

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
async def fetch_jwks(url: str) -> dict | None:
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(url)
            response.raise_for_status()
            result = response.json()
            return result
    except Exception as e:
        logger.error(f"Failed to fetch JWKS: {e}")
        raise HTTPException(status_code=503, detail="JWKS temporarily unavailable")


async def get_auth_jwks() -> dict | None:
    if not settings.auth_jwks:
        return None
    return await fetch_jwks(settings.auth_jwks)


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
    if not jwks:
        raise HTTPException(status_code=401, detail="JWKS not found")

    try:
        claims = jwt.decode(token, jwks)
        claims.validate()
        return claims

    except HTTPException:
        raise

    except Exception as e:
        logger.error(f"JWT error: {e}")
        raise HTTPException(status_code=401, detail="Invalid token")
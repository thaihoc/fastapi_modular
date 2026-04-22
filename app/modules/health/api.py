from datetime import datetime, timezone

from fastapi import APIRouter
from sqlalchemy import text

from app.core.cache import get_redis_client
from app.db.session import SessionLocal

from .schemas import ComponentStatus, HealthResponse, ReadinessResponse

router = APIRouter(prefix="/health", tags=["Health"])


@router.get("", response_model=HealthResponse)
def liveness():
    return HealthResponse(status="ok", timestamp=datetime.now(timezone.utc))


@router.get("/ready", response_model=ReadinessResponse)
def readiness():
    checks: dict[str, ComponentStatus] = {}

    # Database check
    try:
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        checks["database"] = ComponentStatus(status="ok")
    except Exception as e:
        checks["database"] = ComponentStatus(status="error", detail=str(e))

    # Redis check
    redis = get_redis_client()
    if redis is not None:
        try:
            redis.ping()
            checks["redis"] = ComponentStatus(status="ok")
        except Exception as e:
            checks["redis"] = ComponentStatus(status="error", detail=str(e))
    else:
        checks["redis"] = ComponentStatus(status="ok", detail="not configured, using in-memory cache")

    overall = "ok" if all(c.status == "ok" for c in checks.values()) else "error"
    return ReadinessResponse(
        status=overall,
        timestamp=datetime.now(timezone.utc),
        checks=checks,
    )

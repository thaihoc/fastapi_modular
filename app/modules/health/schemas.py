from datetime import datetime
from typing import Literal

from pydantic import BaseModel


class ComponentStatus(BaseModel):
    status: Literal["ok", "error"]
    detail: str | None = None


class HealthResponse(BaseModel):
    status: Literal["ok", "error"]
    timestamp: datetime


class ReadinessResponse(BaseModel):
    status: Literal["ok", "degraded", "error"]
    timestamp: datetime
    checks: dict[str, ComponentStatus]

from fastapi import FastAPI
from app.modules.users.api import router as user_router
from app.core.config import settings
from app.core.router_loader import register_routers

app = FastAPI(title=settings.project_name, debug=settings.debug)

register_routers(app)


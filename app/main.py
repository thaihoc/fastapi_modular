from fastapi import FastAPI
from app.modules.users.api import router as user_router
from app.core.config import settings
from app.core.cache import init_cache
from app.core.router_loader import register_routers

app = FastAPI(title=settings.project_name, debug=settings.debug, on_startup=[init_cache])

register_routers(app)


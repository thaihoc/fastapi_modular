import importlib
import pkgutil
import app.modules
from fastapi import FastAPI

def register_routers(fastapi: FastAPI, api_prefix: str = "/api/v1"):
    for _, module_name, _ in pkgutil.iter_modules(app.modules.__path__):
        module_path = f"app.modules.{module_name}.api"

        try:
            module = importlib.import_module(module_path)
        except ModuleNotFoundError:
            continue
        except Exception as e:
            print(f"[ERROR] loading router for module {module_name}: {e}")
            continue

        router = getattr(module, "router", None)

        if router:
            fastapi.include_router(router, prefix=api_prefix)
        else:
            print(f"[WARNING] {module_name} has no router")
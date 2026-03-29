from sqlalchemy.orm import declarative_base

Base = declarative_base()

import importlib
import pkgutil
import app.modules

def load_all_models():
    for _, module_name, _ in pkgutil.iter_modules(app.modules.__path__):
        try:
            importlib.import_module(f"app.modules.{module_name}.models")
        except ModuleNotFoundError:
            pass

load_all_models()
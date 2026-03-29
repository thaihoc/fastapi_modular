import importlib
import pkgutil
import app.modules

def load_models():
    for _, module_name, _ in pkgutil.iter_modules(app.modules.__path__):
        try:
            importlib.import_module(f"app.modules.{module_name}.models")
        except ModuleNotFoundError:
            pass
        except Exception as e:
            print(f"[ERROR] loading model for module {module_name}: {e}")
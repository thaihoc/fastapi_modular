import importlib
import pkgutil
import app.modules


def register_dependencies():
    for _, module_name, _ in pkgutil.iter_modules(app.modules.__path__):
        try:
            importlib.import_module(f"app.modules.{module_name}.deps")
        except ModuleNotFoundError:
            continue
        except Exception as e:
            print(f"[ERROR] loading {module_name}: {e}")
            continue
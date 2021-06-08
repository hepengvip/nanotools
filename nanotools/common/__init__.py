import os
import json


def ensure_dir(path, create=False):
    if not path:
        return False
    if not create:
        return os.path.isdir(path)
    if os.path.exists(path):
        if os.path.isdir(path):
            return True
        return False
    try:
        os.makedirs(path)
    except OSError:
        return False
    except Exception:
        return False
    return True


def safe_loads(json_body, on_exception=None):
    try:
        return json.loads(json_body)
    except Exception:
        return on_exception

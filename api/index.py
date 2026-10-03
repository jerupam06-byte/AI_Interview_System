import sys
from pathlib import Path

# Add project root directory to sys.path so app and its modules are discoverable
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app import app


class PathFixerMiddleware:
    """Ensure Vercel serverless function prefixes in PATH_INFO are cleanly stripped."""
    def __init__(self, wsgi_app):
        self.wsgi_app = wsgi_app

    def __call__(self, environ, start_response):
        path_info = environ.get("PATH_INFO", "")
        if path_info in ("/api", "/api/index", "/api/index.py"):
            environ["PATH_INFO"] = "/"
        else:
            for prefix in ("/api/index.py/", "/api/index/", "/api/"):
                if path_info.startswith(prefix):
                    environ["PATH_INFO"] = "/" + path_info[len(prefix):]
                    break

        return self.wsgi_app(environ, start_response)


app.wsgi_app = PathFixerMiddleware(app.wsgi_app)

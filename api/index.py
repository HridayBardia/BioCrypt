import os
import sys
import urllib.parse

# Ensure the project root directory is on the Python path
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from app import app as fastapi_app


class VercelPathMiddleware:
    """Pure ASGI middleware that runs before Starlette routing to normalize Vercel serverless paths."""
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            headers = dict(scope.get("headers", []))
            target = None

            # 1. Check for original path headers injected by Vercel
            for k, v in headers.items():
                if k.lower() in [b"x-matched-path", b"x-forwarded-uri", b"x-invoke-path", b"x-original-url"]:
                    target = v.decode("latin1")
                    break

            # 2. Check for path captured via vercel.json rewrite query string (?path=/...)
            qs = scope.get("query_string", b"").decode("latin1")
            if not target and "path=" in qs:
                params = urllib.parse.parse_qs(qs)
                if "path" in params and params["path"]:
                    target = params["path"][0]

            if target:
                clean = target.split("?")[0]
                if clean in ["", "/", "/api", "/api/", "/api/index", "/api/index.py"]:
                    clean = "/"
                scope["path"] = clean
            else:
                p = scope.get("path", "")
                if p in ["", "/", "/api", "/api/", "/api/index", "/api/index.py"]:
                    scope["path"] = "/"
                elif p.startswith("/api/index.py/"):
                    scope["path"] = p[len("/api/index.py"):]

        await self.app(scope, receive, send)


app = VercelPathMiddleware(fastapi_app)

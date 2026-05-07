import uuid
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from core.logging import REQUEST_ID_CTX


class RequestIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        token = REQUEST_ID_CTX.set(request_id)
        try:
            response = await call_next(request)
        finally:
            REQUEST_ID_CTX.reset(token)
        response.headers["X-Request-ID"] = request_id
        return response

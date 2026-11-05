"""Guardrails middleware - input/output safety screening for all API requests."""
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
import re
import logging

logger = logging.getLogger(__name__)

# Blocked patterns (basic guardrails - extend with NeMo Guardrails in production)
BLOCKED_PATTERNS = [
    r"<script[^>]*>",
    r"javascript:",
    r"eval\(",
    r"exec\(",
    r"__import__",
    r"DROP TABLE",
    r"SELECT .* FROM",
]

# Maximum request body size (1MB)
MAX_BODY_SIZE = 1_048_576


class GuardrailsMiddleware(BaseHTTPMiddleware):
    """
    Middleware to screen all API requests for injection attacks and policy violations.
    In production, integrate NeMo Guardrails for LLM-specific content filtering.
    """

    async def dispatch(self, request: Request, call_next):
        # Skip guardrails for health check and docs
        if request.url.path in ["/health", "/docs", "/redoc", "/openapi.json"]:
            return await call_next(request)

        # Check content length
        content_length = request.headers.get("content-length")
        if content_length and int(content_length) > MAX_BODY_SIZE:
            return JSONResponse(
                {"error": "Request body too large", "code": "GUARDRAIL_SIZE"},
                status_code=413,
            )

        # Screen request body for injection patterns
        if request.method in ["POST", "PUT", "PATCH"]:
            try:
                body = await request.body()
                body_str = body.decode("utf-8", errors="ignore")
                for pattern in BLOCKED_PATTERNS:
                    if re.search(pattern, body_str, re.IGNORECASE):
                        logger.warning(
                            f"[GUARDRAIL] Blocked request from {request.client.host}: "
                            f"pattern={pattern} path={request.url.path}"
                        )
                        return JSONResponse(
                            {"error": "Request blocked by safety guardrails", "code": "GUARDRAIL_BLOCKED"},
                            status_code=400,
                        )
            except Exception as e:
                logger.debug(f"Guardrail body check skipped: {e}")

        response = await call_next(request)
        return response

import time
import logging
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

# Standard runtime logger configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("API_Infrastructure")

class ResponseTimingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Route processing phase
        response = await call_next(request)
        
        process_time = time.time() - start_time
        response.headers["X-Process-Time-Ms"] = str(round(process_time * 1000, 2))
        
        logger.info(
            f"Method: {request.method} | Path: {request.url.path} "
            f"| Status: {response.status_code} | Duration: {round(process_time * 1000, 2)}ms"
        )
        return response

# Middleware Configuration

## CORS Configuration

By default, CORS is set to allow all origins (`*`). For production, you should restrict this:

### Update `app/core/middleware.py` CORS settings:

```python
# Development
allow_origins = ["*"]

# Production
allow_origins = [
    "https://yourdomain.com",
    "https://www.yourdomain.com",
    "https://app.yourdomain.com"
]
```

## Available Middleware

### 1. RequestIDMiddleware
- Generates unique ID for each request
- Adds `X-Request-ID` header to responses
- Useful for request tracing and debugging

### 2. LoggingMiddleware
- Logs all incoming requests with method, path, and client IP
- Logs response status code and processing time
- Adds `X-Process-Time` header to responses

### 3. SecurityHeadersMiddleware
Adds security headers:
- `X-Content-Type-Options: nosniff` - Prevents MIME type sniffing
- `X-Frame-Options: DENY` - Prevents clickjacking
- `X-XSS-Protection: 1; mode=block` - XSS protection
- `Strict-Transport-Security` - HTTPS enforcement
- `Content-Security-Policy` - CSP header

### 4. ErrorHandlingMiddleware
- Catches unhandled exceptions
- Returns formatted error response with request ID
- Logs errors with full traceback

### 5. CORSMiddleware
- Handles Cross-Origin Resource Sharing
- Allows requests from configured origins
- Exposes custom headers

## Custom Header Examples

Requests and responses include:
- `X-Request-ID` - Unique request identifier
- `X-Process-Time` - Processing time in seconds
- `X-Content-Type-Options` - Security header
- `X-Frame-Options` - Security header

## Accessing Request ID in Route Handlers

```python
from fastapi import Request

@app.get("/example")
def example(request: Request):
    request_id = getattr(request.state, 'request_id', 'unknown')
    return {"request_id": request_id}
```

## Customizing Middleware Order

The order of middleware execution matters. Currently:
1. ErrorHandlingMiddleware (outermost)
2. RequestIDMiddleware
3. LoggingMiddleware
4. SecurityHeadersMiddleware (innermost)

To change order, modify the order of `add_middleware()` calls in `setup_custom_middleware()`.

## Environment-Specific Configuration

You can modify middleware behavior based on environment:

```python
from app.core.config import settings

def setup_cors_middleware(app):
    origins = ["*"] if settings.DEBUG else ["https://yourdomain.com"]
    app.add_middleware(CORSMiddleware, allow_origins=origins, ...)
```

## Disabling Specific Middleware

Comment out the middleware setup calls in `setup_custom_middleware()`:

```python
def setup_custom_middleware(app):
    # app.add_middleware(LoggingMiddleware)  # Disabled
    app.add_middleware(SecurityHeadersMiddleware)
```

## Testing Middleware

```bash
# View request/response logging
docker-compose logs -f web

# Check response headers
curl -i http://localhost:8000/health

# Check request ID
curl -I http://localhost:8000/docs
```

## Performance Considerations

- LoggingMiddleware adds minimal overhead (millisecond level)
- SecurityHeadersMiddleware is very lightweight
- For high-traffic applications, consider using log aggregation services
- Consider increasing log verbosity only in development

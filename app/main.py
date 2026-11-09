
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from app.config import settings

from app.database import Base, engine
from app.routes.auth import router as auth_router
from app.routes.records import router as records_router


# Create database tables
Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="Nestack Secure Records API",
    description="Secure multi-tenant Records API with authentication and access control",
    version="1.0.0"
)


# Convert validation errors from 422 to 400
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    return JSONResponse(
        status_code=400,
        content=jsonable_encoder({
            "error": "Bad Request",
            "details": exc.errors()
        })
    )


# ASGI middleware to enforce maximum request body size
class RequestSizeLimitMiddleware:

    def __init__(self, app, max_size=16 * 1024):
        self.app = app
        self.max_size = max_size

    async def __call__(self, scope, receive, send):

        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        headers = {
            key.lower(): value
            for key, value in scope.get("headers", [])
        }

        content_length = headers.get(b"content-length")

        if content_length:
            try:
                length = int(content_length)
            except ValueError:
                await self.send_error(
                    send, 400, "Invalid Content-Length"
                )
                return

            if length < 0:
                await self.send_error(
                    send, 400, "Invalid Content-Length"
                )
                return

            if length > self.max_size:
                await self.send_error(
                    send, 413, "Request body too large"
                )
                return

        body = bytearray()

        while True:
            message = await receive()

            if message["type"] == "http.disconnect":
                return

            if message["type"] != "http.request":
                continue

            body.extend(message.get("body", b""))

            if len(body) > self.max_size:
                await self.send_error(
                    send, 413, "Request body too large"
                )
                return

            if not message.get("more_body", False):
                break

        body_bytes = bytes(body)
        body_sent = False

        async def replay_receive():
            nonlocal body_sent

            if not body_sent:
                body_sent = True
                return {
                    "type": "http.request",
                    "body": body_bytes,
                    "more_body": False
                }

            return {
                "type": "http.request",
                "body": b"",
                "more_body": False
            }

        await self.app(scope, replay_receive, send)

    async def send_error(self, send, status_code, message):
        import json

        body = json.dumps({"detail": message}).encode("utf-8")

        await send({
            "type": "http.response.start",
            "status": status_code,
            "headers": [
                (b"content-type", b"application/json"),
                (b"content-length", str(len(body)).encode("ascii"))
            ]
        })

        await send({
            "type": "http.response.body",
            "body": body
        })


# Maximum request body: 16 KB
app.add_middleware(
    RequestSizeLimitMiddleware,
    max_size=settings.MAX_REQUEST_SIZE
)


# Register API routers
app.include_router(auth_router)
app.include_router(records_router)


@app.get("/")
def home():
    return {
        "message": "Nestack Secure Records API is running",
        "status": "active"
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }

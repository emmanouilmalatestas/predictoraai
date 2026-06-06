from starlette.requests import Request
from src.events.producer import EventProducer


class EventMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)

        request = Request(scope, receive=receive)

        # Capture status code
        status_holder = {}

        async def send_wrapper(message):
            if message["type"] == "http.response.start":
                status_holder["status"] = message["status"]
            await send(message)

        # Execute downstream app
        await self.app(scope, receive, send_wrapper)

        # Get pool dynamically from app.state
        pool = request.app.state.pool

        # Publish event AFTER response
        try:
            producer = EventProducer(pool)
            await producer.publish(
                event_type="api.request",
                payload={
                    "path": request.url.path,
                    "method": request.method,
                    "status_code": status_holder.get("status"),
                },
            )
        except Exception:
            pass

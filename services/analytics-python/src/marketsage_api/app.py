from hmac import compare_digest

from fastapi import FastAPI, Request
from starlette.responses import JSONResponse

from marketsage_api.routes import router
from marketsage_core.config import Settings


def create_app() -> FastAPI:
    app = FastAPI(
        title="MarketSage Analytics Core",
        version="0.1.0",
        summary="OpenBB and Hugging Face analytics core behind the MarketSage MCP gateway.",
    )

    @app.middleware("http")
    async def require_bearer_token(request: Request, call_next):
        try:
            settings = Settings.from_env()
        except ValueError as exc:
            return JSONResponse(status_code=500, content={"detail": str(exc)})

        if settings.http_token:
            expected = f"Bearer {settings.http_token}"
            supplied = request.headers.get("authorization", "")
            if not compare_digest(supplied, expected):
                return JSONResponse(
                    status_code=401,
                    content={"detail": "Missing or invalid bearer token"},
                    headers={"www-authenticate": "Bearer"},
                )

        return await call_next(request)

    app.include_router(router)
    return app


app = create_app()

from fastapi import FastAPI
from sqlalchemy import text

from app.api.deps import DBSessionDep
from app.api.v1.router import api_router
from app.core.config import settings

app = FastAPI(
    title=settings.app_name,
    debug=settings.debug,
)

app.include_router(
    api_router,
    prefix="/api/v1",
)


@app.get("/health")
async def health_check(
    db: DBSessionDep,
) -> dict[str, str]:
    await db.execute(text("SELECT 1"))

    return {
        "status": "ok",
        "database": "connected",
        "application": settings.app_name,
    }

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.core.config import settings


app = FastAPI(
    title=settings.app_name,
    description=(
        "YeS-TR proje belgeleri analiz "
        "ve karar destek API'si"
    ),
    version="0.2.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        settings.frontend_url,
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(
    api_router,
    prefix="/api",
)


@app.get("/")
def root() -> dict[str, str]:
    return {
        "application": settings.app_name,
        "status": "running",
        "version": "0.2.0",
    }
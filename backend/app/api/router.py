from fastapi import APIRouter

from app.api.routes.documents import (
    router as documents_router,
)
from app.api.routes.health import (
    router as health_router,
)
from app.api.routes.search import (
    router as search_router,
)
from app.api.routes.auth import (
    router as auth_router,
)
from app.api.routes.answers import (
    router as answers_router,
)
from app.api.routes.conversations import (
    router as conversations_router,
)

api_router = APIRouter()

api_router.include_router(
    health_router,
    prefix="/health",
    tags=["Health"],
)

api_router.include_router(
    documents_router,
    tags=["Documents"],
)

api_router.include_router(
    search_router,
    tags=["Search"],
)

api_router.include_router(
    auth_router,
    prefix="/auth",
    tags=["Auth"],
)

api_router.include_router(
    answers_router,
    tags=["Answers"],
)
api_router.include_router(
    conversations_router,
    tags=["Conversations"],
)
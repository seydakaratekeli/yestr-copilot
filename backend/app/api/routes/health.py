from datetime import datetime, timezone

from fastapi import APIRouter

router = APIRouter()


@router.get("")
def health_check() -> dict:
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
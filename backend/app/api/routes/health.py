from datetime import datetime, timezone

from fastapi import APIRouter

from app.core.config import settings
from app.services.ocr_service import (
    OcrError,
    validate_ocr_configuration,
)


router = APIRouter()


@router.get("")
def health_check() -> dict:
    return {
        "status": "healthy",
        "timestamp": datetime.now(
            timezone.utc
        ).isoformat(),
    }


@router.get("/ocr")
def ocr_health_check() -> dict:
    if not settings.ocr_enabled:
        return {
            "status": "disabled",
            "languages": (
                settings.ocr_languages
            ),
        }

    try:
        validate_ocr_configuration()

        return {
            "status": "healthy",
            "languages": (
                settings.ocr_languages
            ),
            "dpi": settings.ocr_dpi,
            "tessdata_path": (
                settings.tessdata_path
            ),
        }

    except OcrError as exc:
        return {
            "status": "unhealthy",
            "message": str(exc),
            "languages": (
                settings.ocr_languages
            ),
            "tessdata_path": (
                settings.tessdata_path
            ),
        }
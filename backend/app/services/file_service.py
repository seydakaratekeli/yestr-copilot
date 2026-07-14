import re
import unicodedata
from pathlib import Path
from uuid import uuid4


def sanitize_filename(filename: str | None) -> str:
    if not filename:
        return "document.pdf"

    original_path = Path(filename)

    stem = original_path.stem
    suffix = original_path.suffix.lower()

    normalized = unicodedata.normalize("NFKD", stem)
    ascii_name = normalized.encode(
        "ascii",
        "ignore",
    ).decode("ascii")

    safe_stem = re.sub(
        r"[^a-zA-Z0-9_-]+",
        "-",
        ascii_name,
    ).strip("-_")

    if not safe_stem:
        safe_stem = "document"

    if suffix != ".pdf":
        suffix = ".pdf"

    return f"{safe_stem[:80]}{suffix}"


def build_storage_path(
    *,
    user_id: str,
    project_id: str,
    document_id: str | None = None,
    filename: str,
) -> tuple[str, str]:
    final_document_id = document_id or str(uuid4())

    safe_filename = sanitize_filename(filename)

    storage_path = (
        f"users/{user_id}/"
        f"projects/{project_id}/"
        f"{final_document_id}/"
        f"{safe_filename}"
    )

    return final_document_id, storage_path
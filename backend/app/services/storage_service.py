from supabase import Client


class StorageUploadError(RuntimeError):
    pass


def upload_pdf_to_storage(
    *,
    supabase: Client,
    bucket: str,
    storage_path: str,
    content: bytes,
) -> None:
    try:
        supabase.storage.from_(bucket).upload(
            path=storage_path,
            file=content,
            file_options={
                "content-type": "application/pdf",
                "cache-control": "3600",
                "upsert": "false",
            },
        )
    except Exception as exc:
        raise StorageUploadError(
            "PDF Storage alanına yüklenemedi."
        ) from exc


def remove_file_from_storage(
    *,
    supabase: Client,
    bucket: str,
    storage_path: str,
) -> None:
    try:
        supabase.storage.from_(bucket).remove(
            [storage_path]
        )
    except Exception:
        # Temizleme hatası ana hatayı gölgelememeli.
        pass

class StorageDownloadError(RuntimeError):
    pass


def download_file_from_storage(
    *,
    supabase: Client,
    bucket: str,
    storage_path: str,
) -> bytes:
    try:
        response = (
            supabase.storage
            .from_(bucket)
            .download(storage_path)
        )

        if isinstance(response, bytes):
            return response

        if hasattr(response, "content"):
            return bytes(response.content)

        return bytes(response)

    except Exception as exc:
        raise StorageDownloadError(
            "PDF Storage alanından indirilemedi."
        ) from exc 
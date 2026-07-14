from functools import lru_cache

from supabase import Client, create_client

from app.core.config import settings


@lru_cache
def get_supabase_admin() -> Client:
    """
    Service Role kullanan yönetici istemcisi.

    Yalnızca backend tarafında kullanılmalıdır.
    """
    return create_client(
        settings.supabase_url,
        settings.supabase_service_role_key,
    )


@lru_cache
def get_supabase_auth_client() -> Client:
    """
    Kullanıcı access token'ını doğrulamak için kullanılan istemci.
    """
    return create_client(
        settings.supabase_url,
        settings.supabase_anon_key,
    )
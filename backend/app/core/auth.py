from dataclasses import dataclass

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.supabase import get_supabase_auth_client


security = HTTPBearer(
    auto_error=False,
)


@dataclass(frozen=True)
class AuthenticatedUser:
    id: str
    email: str | None


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(
        security
    ),
) -> AuthenticatedUser:
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Kimlik doğrulama bilgisi bulunamadı.",
        )

    if credentials.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Geçersiz kimlik doğrulama yöntemi.",
        )

    token = credentials.credentials.strip()

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Access token bulunamadı.",
        )

    try:
        supabase = get_supabase_auth_client()

        response = supabase.auth.get_user(token)

        user = response.user

        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Geçersiz veya süresi dolmuş oturum.",
            )

        return AuthenticatedUser(
            id=str(user.id),
            email=user.email,
        )

    except HTTPException:
        raise

    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Oturum doğrulanamadı.",
        ) from exc
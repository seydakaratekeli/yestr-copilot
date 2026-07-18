from fastapi import APIRouter, HTTPException, status, Depends
from app.schemas.auth import LoginRequest, TokenResponse, UserUpdateRequest
from app.core.supabase import get_supabase_auth_client, get_supabase_admin
from app.core.auth import AuthenticatedUser, get_current_user

router = APIRouter()

@router.post("/login", response_model=TokenResponse)
async def login(credentials: LoginRequest):
    supabase = get_supabase_auth_client()
    
    try:
        response = supabase.auth.sign_in_with_password({
            "email": credentials.email,
            "password": credentials.password
        })
        
        if not response.session:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Geçersiz e-posta veya şifre",
            )
            
        return TokenResponse(
            access_token=response.session.access_token,
            token_type="bearer"
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Giriş başarısız. Lütfen bilgilerinizi kontrol edin.",
        )

@router.post("/logout")
async def logout(current_user: AuthenticatedUser = Depends(get_current_user)):
    # Supabase JWT tokens are typically stateless and discarded by the client.
    # If using server-side sessions or blacklists, implement token invalidation here.
    return {"message": "Başarıyla çıkış yapıldı."}

@router.put("/profile")
async def update_profile(
    update_data: UserUpdateRequest,
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    supabase = get_supabase_admin()
    
    try:
        attrs = update_data.model_dump(exclude_unset=True)
        if not attrs:
            return {"message": "Değiştirilecek veri bulunamadı."}
            
        response = supabase.auth.admin.update_user_by_id(current_user.id, attrs)
        return {
            "message": "Kullanıcı bilgileri güncellendi.",
            "user": response.user.model_dump() if response.user else None
        }
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Kullanıcı güncellenirken hata oluştu: {str(exc)}"
        )

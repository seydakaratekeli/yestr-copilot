from pydantic import BaseModel, EmailStr

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class UserUpdateRequest(BaseModel):
    email: str | None = None
    password: str | None = None
    user_metadata: dict | None = None

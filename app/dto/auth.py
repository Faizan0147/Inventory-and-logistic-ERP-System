"""
Pydantic DTOs for authentication, registration requests, and users.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr


# ── Registration Request DTOs ────────────────────────────────────────

class RegistrationRequestCreate(BaseModel):
    name: str
    email: EmailStr
    phone: Optional[str] = None
    company_name: Optional[str] = None
    message: Optional[str] = None


class RegistrationRequestRead(BaseModel):
    request_id: str
    name: str
    email: EmailStr
    phone: Optional[str] = None
    company_name: Optional[str] = None
    message: Optional[str] = None
    status: str
    created_at: datetime


class ApproveRequestBody(BaseModel):
    role: str  # "SUPERADMIN" or "SUPPLIER"


# ── Login / Token DTOs ───────────────────────────────────────────────

class LoginRequest(BaseModel):
    email: EmailStr
    password: str
    
class AuthUser(BaseModel):
    user_id: str
    name: str
    email: str
    role: str

class TokenResponse(BaseModel):
    access_token: str
    user: AuthUser
    user: AuthUser
    token_type: str = "bearer"

# ── User DTOs ────────────────────────────────────────────────────────

class UserRead(BaseModel):
    user_id: str
    name: str
    email: EmailStr
    role: str
    is_active: bool

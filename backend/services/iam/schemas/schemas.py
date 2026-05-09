from pydantic import BaseModel, EmailStr
from typing import Optional, Dict, Any

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    user_id: Optional[int] = None
    organization_id: Optional[int] = None

class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    password: str
    organization_id: Optional[int] = None

class UserResponse(UserBase):
    id: int
    organization_id: int
    class Config:
        orm_mode = True

class OrganizationBase(BaseModel):
    name: str
    slug: str
    config: Optional[Dict[str, Any]] = {}

class OrganizationCreate(OrganizationBase):
    pass

class OrganizationResponse(OrganizationBase):
    id: int
    class Config:
        orm_mode = True

class PasswordReset(BaseModel):
    email: EmailStr

class PasswordChange(BaseModel):
    old_password: str
    new_password: str

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = None

class OrganizationUpdate(BaseModel):
    name: Optional[str] = None
    slug: Optional[str] = None
    config: Optional[Dict[str, Any]] = None

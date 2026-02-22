"""
User schemas for request/response validation
"""
from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional
from datetime import datetime
import uuid


class UserBase(BaseModel):
    """Base user schema"""
    email: EmailStr


class UserCreate(UserBase):
    """User creation schema"""
    password: str


class UserLogin(BaseModel):
    """User login schema"""
    email: EmailStr
    password: str


class UserResponse(UserBase):
    """User response schema"""
    id: uuid.UUID
    is_active: bool
    created_at: datetime
    
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True
    )
    
    @classmethod
    def model_validate(cls, obj):
        """Custom validation to map PascalCase model attributes to snake_case schema fields"""
        if hasattr(obj, 'UserId'):
            return cls(
                email=obj.Email,
                id=obj.UserId,
                is_active=obj.IsActive,
                created_at=obj.DateCreated
            )
        return super().model_validate(obj)


class Token(BaseModel):
    """Token response schema"""
    access_token: str
    token_type: str


class TokenData(BaseModel):
    """Token data schema"""
    user_id: Optional[str] = None

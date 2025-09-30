"""
User repository for data access
"""
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.user import User


class UserRepository:
    """User repository for data access operations"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_user(self, email: str, password_hash: str) -> User:
        """Create a new user"""
        user = User(email=email, password_hash=password_hash)
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user
    
    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        result = await self.db.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()
    
    async def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID"""
        result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()
    
    async def update_user(self, user: User) -> User:
        """Update user"""
        await self.db.commit()
        await self.db.refresh(user)
        return user
    
    async def delete_user(self, user: User) -> None:
        """Delete user"""
        await self.db.delete(user)
        await self.db.commit()

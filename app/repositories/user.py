from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.user import User


class UserRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_by_email(
        self,
        email: str,
    ) -> User | None:
        statement = (
            select(User).options(selectinload(User.role)).where(User.email == email)
        )

        result = await self.db.execute(statement)

        return result.scalar_one_or_none()

    async def create(
        self,
        *,
        full_name: str,
        email: str,
        password_hash: str,
        role_id: int,
    ) -> User:
        user = User(
            full_name=full_name,
            email=email,
            password_hash=password_hash,
            role_id=role_id,
        )

        self.db.add(user)
        await self.db.flush()

        return user

    async def get_by_id(
        self,
        user_id: int,
    ) -> User | None:
        statement = (
            select(User).options(selectinload(User.role)).where(User.id == user_id)
        )

        result = await self.db.execute(statement)

        return result.scalar_one_or_none()

    async def get_all(
        self,
        *,
        offset: int = 0,
        limit: int = 100,
    ) -> list[User]:
        statement = (
            select(User)
            .options(selectinload(User.role))
            .order_by(User.id)
            .offset(offset)
            .limit(limit)
        )

        result = await self.db.execute(statement)

        return list(result.scalars().all())

    async def set_active_status(
        self,
        user: User,
        *,
        is_active: bool,
    ) -> User:
        user.is_active = is_active

        await self.db.flush()

        return user

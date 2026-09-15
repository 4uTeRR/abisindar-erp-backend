from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import (
    CannotDeactivateSelfError,
    RoleNotFoundError,
    UserAlreadyExistsError,
    UserNotFoundError,
)
from app.core.security import hash_password
from app.models.user import User
from app.repositories.role import RoleRepository
from app.repositories.user import UserRepository
from app.schemas.user import UserCreate


class UserService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.user_repository = UserRepository(db)
        self.role_repository = RoleRepository(db)

    async def create_user(
        self,
        data: UserCreate,
    ) -> User:
        email = str(data.email).strip().lower()
        role_name = data.role_name.strip().lower()
        full_name = data.full_name.strip()

        existing_user = await self.user_repository.get_by_email(
            email,
        )

        if existing_user is not None:
            raise UserAlreadyExistsError

        role = await self.role_repository.get_by_name(
            role_name,
        )

        if role is None:
            raise RoleNotFoundError

        hashed_password = hash_password(data.password)

        try:
            user = await self.user_repository.create(
                full_name=full_name,
                email=email,
                password_hash=hashed_password,
                role_id=role.id,
            )

            await self.db.commit()

        except IntegrityError as exc:
            await self.db.rollback()
            raise UserAlreadyExistsError from exc

        await self.db.refresh(user)

        return user

    async def get_users(
        self,
        *,
        offset: int = 0,
        limit: int = 100,
    ) -> list[User]:
        return await self.user_repository.get_all(
            offset=offset,
            limit=limit,
        )

    async def set_user_status(
        self,
        *,
        user_id: int,
        is_active: bool,
        current_user_id: int,
    ) -> User:
        user = await self.user_repository.get_by_id(user_id)

        if user is None:
            raise UserNotFoundError

        if user.id == current_user_id and not is_active:
            raise CannotDeactivateSelfError

        await self.user_repository.set_active_status(
            user,
            is_active=is_active,
        )

        await self.db.commit()

        return user

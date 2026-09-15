from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import InvalidCredentialsError
from app.core.security import create_access_token, verify_password
from app.repositories.user import UserRepository
from app.schemas.auth import LoginRequest


class AuthService:
    def __init__(self, db: AsyncSession) -> None:
        self.user_repository = UserRepository(db)

    async def login(
        self,
        data: LoginRequest,
    ) -> str:
        email = str(data.email).strip().lower()

        user = await self.user_repository.get_by_email(email)

        if user is None:
            raise InvalidCredentialsError

        if not user.is_active:
            raise InvalidCredentialsError

        if not verify_password(
            data.password,
            user.password_hash,
        ):
            raise InvalidCredentialsError

        return create_access_token(user.id)

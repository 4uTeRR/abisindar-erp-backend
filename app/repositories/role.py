from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.role import Role


class RoleRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_by_name(
        self,
        name: str,
    ) -> Role | None:
        statement = select(Role).where(Role.name == name)

        result = await self.db.execute(statement)

        return result.scalar_one_or_none()

    async def create(
        self,
        *,
        name: str,
        description: str | None,
    ) -> Role:
        role = Role(
            name=name,
            description=description,
        )

        self.db.add(role)
        await self.db.flush()

        return role

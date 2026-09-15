from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import RoleAlreadyExistsError
from app.models.role import Role
from app.repositories.role import RoleRepository
from app.schemas.role import RoleCreate


class RoleService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.repository = RoleRepository(db)

    async def create_role(
        self,
        data: RoleCreate,
    ) -> Role:
        name = data.name.strip().lower()

        existing_role = await self.repository.get_by_name(name)

        if existing_role is not None:
            raise RoleAlreadyExistsError

        role = await self.repository.create(
            name=name,
            description=data.description,
        )

        await self.db.commit()
        await self.db.refresh(role)

        return role

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.unit import Unit


class UnitRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_by_id(
        self,
        unit_id: int,
    ) -> Unit | None:
        result = await self.db.execute(select(Unit).where(Unit.id == unit_id))

        return result.scalar_one_or_none()

    async def get_by_code(
        self,
        code: str,
    ) -> Unit | None:
        result = await self.db.execute(select(Unit).where(Unit.code == code))

        return result.scalar_one_or_none()

    async def get_all(self) -> list[Unit]:
        result = await self.db.execute(select(Unit).order_by(Unit.name))

        return list(result.scalars().all())

    async def create(
        self,
        *,
        name: str,
        code: str,
    ) -> Unit:
        unit = Unit(
            name=name,
            code=code,
        )

        self.db.add(unit)
        await self.db.flush()

        return unit

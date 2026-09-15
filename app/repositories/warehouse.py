from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.warehouse import Warehouse


class WarehouseRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_by_id(
        self,
        warehouse_id: int,
    ) -> Warehouse | None:
        result = await self.db.execute(
            select(Warehouse).where(Warehouse.id == warehouse_id)
        )

        return result.scalar_one_or_none()

    async def get_by_name(
        self,
        name: str,
    ) -> Warehouse | None:
        result = await self.db.execute(select(Warehouse).where(Warehouse.name == name))

        return result.scalar_one_or_none()

    async def get_all(self) -> list[Warehouse]:
        result = await self.db.execute(select(Warehouse).order_by(Warehouse.name))

        return list(result.scalars().all())

    async def create(
        self,
        *,
        name: str,
    ) -> Warehouse:
        warehouse = Warehouse(name=name)

        self.db.add(warehouse)
        await self.db.flush()

        return warehouse

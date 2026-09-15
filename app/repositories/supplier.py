from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.supplier import Supplier


class SupplierRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_by_id(
        self,
        supplier_id: int,
    ) -> Supplier | None:
        result = await self.db.execute(
            select(Supplier).where(Supplier.id == supplier_id)
        )

        return result.scalar_one_or_none()

    async def get_by_code(
        self,
        code: str,
    ) -> Supplier | None:
        result = await self.db.execute(select(Supplier).where(Supplier.code == code))

        return result.scalar_one_or_none()

    async def get_all(
        self,
        *,
        offset: int = 0,
        limit: int = 100,
    ) -> list[Supplier]:
        statement = select(Supplier).order_by(Supplier.name).offset(offset).limit(limit)

        result = await self.db.execute(statement)

        return list(result.scalars().all())

    async def create(
        self,
        supplier: Supplier,
    ) -> Supplier:
        self.db.add(supplier)
        await self.db.flush()

        return supplier

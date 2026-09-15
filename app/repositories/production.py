from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.production_batch import ProductionBatch


class ProductionRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_by_id(
        self,
        batch_id: int,
    ) -> ProductionBatch | None:
        statement = (
            select(ProductionBatch)
            .options(
                selectinload(ProductionBatch.product),
                selectinload(ProductionBatch.warehouse),
            )
            .where(ProductionBatch.id == batch_id)
        )

        result = await self.db.execute(statement)

        return result.scalar_one_or_none()

    async def create(
        self,
        batch: ProductionBatch,
    ) -> ProductionBatch:
        self.db.add(batch)
        await self.db.flush()

        return batch

from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.stock_movement import StockMovement


class StockRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create_movement(
        self,
        movement: StockMovement,
    ) -> StockMovement:
        self.db.add(movement)
        await self.db.flush()

        return movement

    async def get_balance(
        self,
        *,
        product_id: int,
        warehouse_id: int,
    ) -> Decimal:
        statement = select(
            func.coalesce(
                func.sum(StockMovement.quantity_delta),
                0,
            )
        ).where(
            StockMovement.product_id == product_id,
            StockMovement.warehouse_id == warehouse_id,
        )

        result = await self.db.execute(statement)

        value = result.scalar_one()

        return Decimal(value)

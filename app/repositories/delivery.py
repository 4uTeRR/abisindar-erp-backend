from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.delivery import Delivery
from app.models.delivery_item import DeliveryItem


class DeliveryRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create_delivery(
        self,
        delivery: Delivery,
    ) -> Delivery:
        self.db.add(delivery)
        await self.db.flush()

        return delivery

    async def create_item(
        self,
        item: DeliveryItem,
    ) -> DeliveryItem:
        self.db.add(item)
        await self.db.flush()

        return item

    async def get_by_id(
        self,
        delivery_id: int,
    ) -> Delivery | None:
        statement = (
            select(Delivery)
            .options(
                selectinload(Delivery.customer),
                selectinload(Delivery.warehouse),
                selectinload(Delivery.courier),
                selectinload(Delivery.items).selectinload(DeliveryItem.product),
            )
            .where(Delivery.id == delivery_id)
        )

        result = await self.db.execute(statement)

        return result.scalar_one_or_none()

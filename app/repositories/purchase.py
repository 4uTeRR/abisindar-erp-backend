from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.purchase import Purchase
from app.models.purchase_item import PurchaseItem


class PurchaseRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create_purchase(
        self,
        purchase: Purchase,
    ) -> Purchase:
        self.db.add(purchase)
        await self.db.flush()

        return purchase

    async def create_item(
        self,
        item: PurchaseItem,
    ) -> PurchaseItem:
        self.db.add(item)
        await self.db.flush()

        return item

    async def get_by_id(
        self,
        purchase_id: int,
    ) -> Purchase | None:
        statement = (
            select(Purchase)
            .options(
                selectinload(Purchase.supplier),
                selectinload(Purchase.warehouse),
                selectinload(Purchase.items).selectinload(PurchaseItem.product),
            )
            .where(Purchase.id == purchase_id)
        )

        result = await self.db.execute(statement)

        return result.scalar_one_or_none()

    async def get_by_supplier_invoice(
        self,
        *,
        supplier_id: int,
        invoice_number: str,
    ) -> Purchase | None:
        statement = select(Purchase).where(
            Purchase.supplier_id == supplier_id,
            Purchase.invoice_number == invoice_number,
        )

        result = await self.db.execute(statement)

        return result.scalar_one_or_none()

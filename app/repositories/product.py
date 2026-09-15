from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.product import Product


class ProductRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_by_id(
        self,
        product_id: int,
    ) -> Product | None:
        statement = (
            select(Product)
            .options(
                selectinload(Product.base_unit),
                selectinload(Product.category),
            )
            .where(Product.id == product_id)
        )

        result = await self.db.execute(statement)

        return result.scalar_one_or_none()

    async def get_by_sku(
        self,
        sku: str,
    ) -> Product | None:
        statement = select(Product).where(Product.sku == sku)

        result = await self.db.execute(statement)

        return result.scalar_one_or_none()

    async def get_all(
        self,
        *,
        offset: int = 0,
        limit: int = 100,
    ) -> list[Product]:
        statement = (
            select(Product)
            .options(
                selectinload(Product.base_unit),
                selectinload(Product.category),
            )
            .order_by(Product.name)
            .offset(offset)
            .limit(limit)
        )

        result = await self.db.execute(statement)

        return list(result.scalars().all())

    async def create(
        self,
        product: Product,
    ) -> Product:
        self.db.add(product)
        await self.db.flush()

        return product

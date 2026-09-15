from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.customer import Customer


class CustomerRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_by_id(
        self,
        customer_id: int,
    ) -> Customer | None:
        statement = select(Customer).where(Customer.id == customer_id)

        result = await self.db.execute(statement)

        return result.scalar_one_or_none()

    async def get_by_code(
        self,
        code: str,
    ) -> Customer | None:
        statement = select(Customer).where(Customer.code == code)

        result = await self.db.execute(statement)

        return result.scalar_one_or_none()

    async def get_all(
        self,
        *,
        offset: int = 0,
        limit: int = 100,
    ) -> list[Customer]:
        statement = select(Customer).order_by(Customer.name).offset(offset).limit(limit)

        result = await self.db.execute(statement)

        return list(result.scalars().all())

    async def create(
        self,
        customer: Customer,
    ) -> Customer:
        self.db.add(customer)
        await self.db.flush()

        return customer

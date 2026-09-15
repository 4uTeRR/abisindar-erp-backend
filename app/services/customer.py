from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import CustomerAlreadyExistsError
from app.models.customer import Customer
from app.repositories.customer import CustomerRepository
from app.schemas.customer import CustomerCreate


class CustomerService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.repository = CustomerRepository(db)

    async def create_customer(
        self,
        data: CustomerCreate,
    ) -> Customer:
        code = None

        if data.code is not None:
            code = data.code.strip().upper()

            existing = await self.repository.get_by_code(code)

            if existing is not None:
                raise CustomerAlreadyExistsError

        customer = Customer(
            name=data.name.strip(),
            code=code,
            phone=data.phone.strip() if data.phone else None,
            address=data.address.strip() if data.address else None,
        )

        try:
            await self.repository.create(customer)
            await self.db.commit()

        except IntegrityError as exc:
            await self.db.rollback()
            raise CustomerAlreadyExistsError from exc

        return customer

    async def get_customers(
        self,
        *,
        offset: int,
        limit: int,
    ) -> list[Customer]:
        return await self.repository.get_all(
            offset=offset,
            limit=limit,
        )

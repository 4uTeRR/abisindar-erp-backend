from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import SupplierAlreadyExistsError
from app.models.supplier import Supplier
from app.repositories.supplier import SupplierRepository
from app.schemas.supplier import SupplierCreate


class SupplierService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.repository = SupplierRepository(db)

    async def create_supplier(
        self,
        data: SupplierCreate,
    ) -> Supplier:
        name = data.name.strip()

        code = (
            data.code.strip().upper()
            if data.code and data.code.strip()
            else None
        )

        phone = (
            data.phone.strip()
            if data.phone and data.phone.strip()
            else None
        )

        address = (
            data.address.strip()
            if data.address and data.address.strip()
            else None
        )

        if code is not None:
            existing = await self.repository.get_by_code(code)

            if existing is not None:
                raise SupplierAlreadyExistsError

        supplier = Supplier(
            name=name,
            code=code,
            phone=phone,
            address=address,
        )

        try:
            await self.repository.create(supplier)
            await self.db.commit()

        except IntegrityError as exc:
            await self.db.rollback()
            raise SupplierAlreadyExistsError from exc

        return supplier

    async def get_suppliers(
        self,
        *,
        offset: int,
        limit: int,
    ) -> list[Supplier]:
        return await self.repository.get_all(
            offset=offset,
            limit=limit,
        )
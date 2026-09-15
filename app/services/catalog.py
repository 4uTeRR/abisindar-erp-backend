from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import (
    CategoryAlreadyExistsError,
    CategoryNotFoundError,
    ProductAlreadyExistsError,
    UnitAlreadyExistsError,
    UnitNotFoundError,
)
from app.models.category import Category
from app.models.product import Product
from app.models.unit import Unit
from app.repositories.category import CategoryRepository
from app.repositories.product import ProductRepository
from app.repositories.unit import UnitRepository
from app.schemas.catalog import (
    CategoryCreate,
    ProductCreate,
    UnitCreate,
)


class CatalogService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

        self.unit_repository = UnitRepository(db)
        self.category_repository = CategoryRepository(db)
        self.product_repository = ProductRepository(db)

    async def create_unit(
        self,
        data: UnitCreate,
    ) -> Unit:
        code = data.code.strip().lower()
        name = data.name.strip()

        existing = await self.unit_repository.get_by_code(code)

        if existing is not None:
            raise UnitAlreadyExistsError

        try:
            unit = await self.unit_repository.create(
                name=name,
                code=code,
            )

            await self.db.commit()

        except IntegrityError as exc:
            await self.db.rollback()
            raise UnitAlreadyExistsError from exc

        return unit

    async def get_units(self) -> list[Unit]:
        return await self.unit_repository.get_all()

    async def create_category(
        self,
        data: CategoryCreate,
    ) -> Category:
        name = data.name.strip()

        existing = await self.category_repository.get_by_name(
            name,
        )

        if existing is not None:
            raise CategoryAlreadyExistsError

        try:
            category = await self.category_repository.create(
                name=name,
                description=data.description,
            )

            await self.db.commit()

        except IntegrityError as exc:
            await self.db.rollback()
            raise CategoryAlreadyExistsError from exc

        return category

    async def get_categories(self) -> list[Category]:
        return await self.category_repository.get_all()

    async def create_product(
        self,
        data: ProductCreate,
    ) -> Product:
        unit = await self.unit_repository.get_by_id(
            data.base_unit_id,
        )

        if unit is None:
            raise UnitNotFoundError

        category = await self.category_repository.get_by_id(
            data.category_id,
        )

        if category is None:
            raise CategoryNotFoundError

        sku = None

        if data.sku is not None:
            sku = data.sku.strip().upper()

            existing_product = await self.product_repository.get_by_sku(sku)

            if existing_product is not None:
                raise ProductAlreadyExistsError

        product = Product(
            name=data.name.strip(),
            sku=sku,
            product_type=data.product_type,
            base_unit_id=unit.id,
            category_id=category.id,
            package_weight=data.package_weight,
            sale_price=data.sale_price,
        )

        try:
            await self.product_repository.create(product)

            await self.db.commit()

        except IntegrityError as exc:
            await self.db.rollback()
            raise ProductAlreadyExistsError from exc

        created_product = await self.product_repository.get_by_id(product.id)

        if created_product is None:
            raise RuntimeError("Created product could not be loaded")

        return created_product

    async def get_products(
        self,
        *,
        offset: int,
        limit: int,
    ) -> list[Product]:
        return await self.product_repository.get_all(
            offset=offset,
            limit=limit,
        )

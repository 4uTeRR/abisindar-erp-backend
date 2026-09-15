from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import (
    ProductCannotBeProducedError,
    ProductNotFoundError,
    WarehouseAlreadyExistsError,
    WarehouseNotFoundError,
)
from app.models.enums import ProductType, StockMovementType
from app.models.production_batch import ProductionBatch
from app.models.stock_movement import StockMovement
from app.models.warehouse import Warehouse
from app.repositories.product import ProductRepository
from app.repositories.production import ProductionRepository
from app.repositories.stock import StockRepository
from app.repositories.warehouse import WarehouseRepository
from app.schemas.inventory import ProductionBatchCreate, WarehouseCreate


class InventoryService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

        self.product_repository = ProductRepository(db)
        self.warehouse_repository = WarehouseRepository(db)
        self.production_repository = ProductionRepository(db)
        self.stock_repository = StockRepository(db)

    async def create_warehouse(
        self,
        data: WarehouseCreate,
    ) -> Warehouse:
        name = data.name.strip()

        existing = await self.warehouse_repository.get_by_name(
            name,
        )

        if existing is not None:
            raise WarehouseAlreadyExistsError

        warehouse = await self.warehouse_repository.create(
            name=name,
        )

        try:
            await self.db.commit()
        except IntegrityError as exc:
            await self.db.rollback()
            raise WarehouseAlreadyExistsError from exc

        return warehouse

    async def get_warehouses(self) -> list[Warehouse]:
        return await self.warehouse_repository.get_all()

    async def create_production_batch(
        self,
        *,
        data: ProductionBatchCreate,
        user_id: int,
    ) -> ProductionBatch:
        product = await self.product_repository.get_by_id(
            data.product_id,
        )

        if product is None:
            raise ProductNotFoundError

        if not product.is_active or product.product_type != ProductType.FINISHED_GOOD:
            raise ProductCannotBeProducedError

        warehouse = await self.warehouse_repository.get_by_id(
            data.warehouse_id,
        )

        if warehouse is None or not warehouse.is_active:
            raise WarehouseNotFoundError

        batch = ProductionBatch(
            product_id=product.id,
            warehouse_id=warehouse.id,
            quantity=data.quantity,
            package_count=data.package_count,
            note=data.note,
            created_by_id=user_id,
        )

        try:
            await self.production_repository.create(batch)

            movement = StockMovement(
                product_id=product.id,
                warehouse_id=warehouse.id,
                movement_type=StockMovementType.PRODUCTION,
                quantity_delta=data.quantity,
                production_batch_id=batch.id,
                created_by_id=user_id,
                note=data.note,
            )

            await self.stock_repository.create_movement(
                movement,
            )

            await self.db.commit()

        except Exception:
            await self.db.rollback()
            raise

        created_batch = await self.production_repository.get_by_id(
            batch.id,
        )

        if created_batch is None:
            raise RuntimeError("Created production batch could not be loaded")

        return created_batch

    async def get_stock_balance(
        self,
        *,
        product_id: int,
        warehouse_id: int,
    ):
        product = await self.product_repository.get_by_id(
            product_id,
        )

        if product is None:
            raise ProductNotFoundError

        warehouse = await self.warehouse_repository.get_by_id(
            warehouse_id,
        )

        if warehouse is None:
            raise WarehouseNotFoundError

        quantity = await self.stock_repository.get_balance(
            product_id=product.id,
            warehouse_id=warehouse.id,
        )

        return product, warehouse, quantity

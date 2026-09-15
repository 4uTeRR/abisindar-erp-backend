from decimal import Decimal

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import (
    DuplicatePurchaseProductError,
    ProductCannotBePurchasedError,
    ProductNotFoundError,
    PurchaseAlreadyExistsError,
    PurchaseNotFoundError,
    SupplierNotFoundError,
    WarehouseNotFoundError,
)
from app.models.enums import ProductType, StockMovementType
from app.models.product import Product
from app.models.purchase import Purchase
from app.models.purchase_item import PurchaseItem
from app.models.stock_movement import StockMovement
from app.repositories.product import ProductRepository
from app.repositories.purchase import PurchaseRepository
from app.repositories.stock import StockRepository
from app.repositories.supplier import SupplierRepository
from app.repositories.warehouse import WarehouseRepository
from app.schemas.purchase import PurchaseCreate


class PurchaseService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

        self.supplier_repository = SupplierRepository(db)
        self.warehouse_repository = WarehouseRepository(db)
        self.product_repository = ProductRepository(db)
        self.purchase_repository = PurchaseRepository(db)
        self.stock_repository = StockRepository(db)

    async def create_purchase(
        self,
        *,
        data: PurchaseCreate,
        created_by_id: int,
    ) -> Purchase:
        supplier = await self.supplier_repository.get_by_id(data.supplier_id)

        if supplier is None or not supplier.is_active:
            raise SupplierNotFoundError

        warehouse = await self.warehouse_repository.get_by_id(data.warehouse_id)

        if warehouse is None or not warehouse.is_active:
            raise WarehouseNotFoundError

        invoice_number = None

        if data.invoice_number is not None:
            invoice_number = data.invoice_number.strip()

            existing = await self.purchase_repository.get_by_supplier_invoice(
                supplier_id=supplier.id,
                invoice_number=invoice_number,
            )

            if existing is not None:
                raise PurchaseAlreadyExistsError

        product_ids = [item.product_id for item in data.items]

        if len(product_ids) != len(set(product_ids)):
            raise DuplicatePurchaseProductError

        prepared_items: list[tuple[Product, Decimal, Decimal]] = []

        for item_data in data.items:
            product = await self.product_repository.get_by_id(item_data.product_id)

            if product is None:
                raise ProductNotFoundError

            if not product.is_active or product.product_type not in {
                ProductType.RAW_MATERIAL,
                ProductType.PACKAGING,
            }:
                raise ProductCannotBePurchasedError

            prepared_items.append(
                (
                    product,
                    item_data.quantity,
                    item_data.unit_price,
                )
            )

        try:
            purchase = Purchase(
                supplier_id=supplier.id,
                warehouse_id=warehouse.id,
                invoice_number=invoice_number,
                created_by_id=created_by_id,
                note=data.note,
            )

            await self.purchase_repository.create_purchase(purchase)

            for product, quantity, unit_price in prepared_items:
                item = PurchaseItem(
                    purchase_id=purchase.id,
                    product_id=product.id,
                    quantity=quantity,
                    unit_price=unit_price,
                )

                await self.purchase_repository.create_item(item)

                movement = StockMovement(
                    product_id=product.id,
                    warehouse_id=warehouse.id,
                    movement_type=StockMovementType.PURCHASE,
                    quantity_delta=quantity,
                    purchase_item_id=item.id,
                    created_by_id=created_by_id,
                    note=data.note,
                )

                await self.stock_repository.create_movement(movement)

            await self.db.commit()

        except IntegrityError as exc:
            await self.db.rollback()
            raise PurchaseAlreadyExistsError from exc

        except Exception:
            await self.db.rollback()
            raise

        created_purchase = await self.purchase_repository.get_by_id(purchase.id)

        if created_purchase is None:
            raise RuntimeError("Created purchase could not be loaded")

        return created_purchase

    async def get_purchase(
        self,
        purchase_id: int,
    ) -> Purchase:
        purchase = await self.purchase_repository.get_by_id(purchase_id)

        if purchase is None:
            raise PurchaseNotFoundError

        return purchase

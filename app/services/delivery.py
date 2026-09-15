from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import (
    CourierNotFoundError,
    CustomerNotFoundError,
    DuplicateDeliveryProductError,
    InsufficientStockError,
    InvalidCourierError,
    ProductCannotBeDeliveredError,
    ProductNotFoundError,
    ProductPriceNotFoundError,
    WarehouseNotFoundError,
)
from app.models.delivery import Delivery
from app.models.delivery_item import DeliveryItem
from app.models.enums import ProductType, StockMovementType
from app.models.product import Product
from app.models.stock_movement import StockMovement
from app.repositories.customer import CustomerRepository
from app.repositories.delivery import DeliveryRepository
from app.repositories.product import ProductRepository
from app.repositories.stock import StockRepository
from app.repositories.user import UserRepository
from app.repositories.warehouse import WarehouseRepository
from app.schemas.delivery import DeliveryCreate


class DeliveryService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

        self.customer_repository = CustomerRepository(db)
        self.warehouse_repository = WarehouseRepository(db)
        self.user_repository = UserRepository(db)
        self.product_repository = ProductRepository(db)
        self.delivery_repository = DeliveryRepository(db)
        self.stock_repository = StockRepository(db)

    async def create_delivery(
        self,
        *,
        data: DeliveryCreate,
        created_by_id: int,
    ) -> Delivery:
        customer = await self.customer_repository.get_by_id(data.customer_id)

        if customer is None or not customer.is_active:
            raise CustomerNotFoundError

        warehouse = await self.warehouse_repository.get_by_id(data.warehouse_id)

        if warehouse is None or not warehouse.is_active:
            raise WarehouseNotFoundError

        courier = await self.user_repository.get_by_id(data.courier_id)

        if courier is None or not courier.is_active:
            raise CourierNotFoundError

        if courier.role.name != "courier":
            raise InvalidCourierError

        product_ids = [item.product_id for item in data.items]

        if len(product_ids) != len(set(product_ids)):
            raise DuplicateDeliveryProductError

        prepared_items: list[tuple[Product, Decimal, Decimal]] = []

        for item_data in data.items:
            product = await self.product_repository.get_by_id(item_data.product_id)

            if product is None:
                raise ProductNotFoundError

            if (
                not product.is_active
                or product.product_type != ProductType.FINISHED_GOOD
            ):
                raise ProductCannotBeDeliveredError

            available_stock = await self.stock_repository.get_balance(
                product_id=product.id,
                warehouse_id=warehouse.id,
            )

            if available_stock < item_data.quantity:
                raise InsufficientStockError

            unit_price = item_data.unit_price

            if unit_price is None:
                unit_price = product.sale_price

            if unit_price is None:
                raise ProductPriceNotFoundError

            prepared_items.append(
                (
                    product,
                    item_data.quantity,
                    unit_price,
                )
            )

        try:
            delivery = Delivery(
                customer_id=customer.id,
                warehouse_id=warehouse.id,
                courier_id=courier.id,
                created_by_id=created_by_id,
                note=data.note,
            )

            await self.delivery_repository.create_delivery(delivery)

            for product, quantity, unit_price in prepared_items:
                item = DeliveryItem(
                    delivery_id=delivery.id,
                    product_id=product.id,
                    quantity=quantity,
                    unit_price=unit_price,
                )

                await self.delivery_repository.create_item(item)

                movement = StockMovement(
                    product_id=product.id,
                    warehouse_id=warehouse.id,
                    movement_type=StockMovementType.DELIVERY,
                    quantity_delta=-quantity,
                    delivery_item_id=item.id,
                    created_by_id=created_by_id,
                    note=data.note,
                )

                await self.stock_repository.create_movement(movement)

            await self.db.commit()

        except Exception:
            await self.db.rollback()
            raise

        created_delivery = await self.delivery_repository.get_by_id(delivery.id)

        if created_delivery is None:
            raise RuntimeError("Created delivery could not be loaded")

        return created_delivery

    async def get_delivery(
        self,
        delivery_id: int,
    ) -> Delivery:
        delivery = await self.delivery_repository.get_by_id(delivery_id)

        if delivery is None:
            from app.core.exceptions import DeliveryNotFoundError

            raise DeliveryNotFoundError

        return delivery

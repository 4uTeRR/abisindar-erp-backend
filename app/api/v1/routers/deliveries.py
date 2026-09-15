from decimal import Decimal

from fastapi import APIRouter, HTTPException, status

from app.api.deps import (
    CurrentUserDep,
    DBSessionDep,
    DeliveryManagerDep,
)
from app.core.exceptions import (
    CourierNotFoundError,
    CustomerNotFoundError,
    DeliveryNotFoundError,
    DuplicateDeliveryProductError,
    InsufficientStockError,
    InvalidCourierError,
    ProductCannotBeDeliveredError,
    ProductNotFoundError,
    ProductPriceNotFoundError,
    WarehouseNotFoundError,
)
from app.models.delivery import Delivery
from app.schemas.delivery import (
    DeliveryCreate,
    DeliveryItemRead,
    DeliveryRead,
)
from app.services.delivery import DeliveryService

router = APIRouter(
    prefix="/deliveries",
    tags=["Deliveries"],
)


def to_delivery_read(
    delivery: Delivery,
) -> DeliveryRead:
    items = [
        DeliveryItemRead(
            id=item.id,
            product_id=item.product_id,
            product_name=item.product.name,
            quantity=item.quantity,
            unit_price=item.unit_price,
            total=item.quantity * item.unit_price,
        )
        for item in delivery.items
    ]

    total_amount = sum(
        (item.total for item in items),
        start=Decimal(0),
    )

    return DeliveryRead(
        id=delivery.id,
        customer_id=delivery.customer_id,
        customer_name=delivery.customer.name,
        warehouse_id=delivery.warehouse_id,
        warehouse_name=delivery.warehouse.name,
        courier_id=delivery.courier_id,
        courier_name=delivery.courier.full_name,
        created_by_id=delivery.created_by_id,
        delivered_at=delivery.delivered_at,
        note=delivery.note,
        items=items,
        total_amount=total_amount,
    )


@router.post(
    "",
    response_model=DeliveryRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_delivery(
    data: DeliveryCreate,
    db: DBSessionDep,
    user: DeliveryManagerDep,
) -> DeliveryRead:
    service = DeliveryService(db)

    try:
        delivery = await service.create_delivery(
            data=data,
            created_by_id=user.id,
        )

    except CustomerNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found",
        ) from exc

    except WarehouseNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Warehouse not found",
        ) from exc

    except CourierNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Courier not found",
        ) from exc

    except InvalidCourierError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Selected user does not have courier role",
        ) from exc

    except ProductNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found",
        ) from exc

    except ProductCannotBeDeliveredError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Only active finished goods can be delivered",
        ) from exc

    except ProductPriceNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Product has no sale price",
        ) from exc

    except InsufficientStockError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Insufficient stock",
        ) from exc

    except DuplicateDeliveryProductError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="A product cannot appear twice in one delivery",
        ) from exc

    return to_delivery_read(delivery)


@router.get(
    "/{delivery_id}",
    response_model=DeliveryRead,
)
async def get_delivery(
    delivery_id: int,
    db: DBSessionDep,
    current_user: CurrentUserDep,
) -> DeliveryRead:
    service = DeliveryService(db)

    try:
        delivery = await service.get_delivery(delivery_id)

    except DeliveryNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Delivery not found",
        ) from exc

    if current_user.role.name == "courier" and delivery.courier_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You cannot access this delivery",
        )

    return to_delivery_read(delivery)

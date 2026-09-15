from decimal import Decimal

from fastapi import APIRouter, HTTPException, status

from app.api.deps import (
    CurrentUserDep,
    DBSessionDep,
    PurchaseManagerDep,
)
from app.core.exceptions import (
    DuplicatePurchaseProductError,
    ProductCannotBePurchasedError,
    ProductNotFoundError,
    PurchaseAlreadyExistsError,
    PurchaseNotFoundError,
    SupplierNotFoundError,
    WarehouseNotFoundError,
)
from app.models.purchase import Purchase
from app.schemas.purchase import (
    PurchaseCreate,
    PurchaseItemRead,
    PurchaseRead,
)
from app.services.purchase import PurchaseService

router = APIRouter(
    prefix="/purchases",
    tags=["Purchases"],
)


def to_purchase_read(
    purchase: Purchase,
) -> PurchaseRead:
    items = [
        PurchaseItemRead(
            id=item.id,
            product_id=item.product_id,
            product_name=item.product.name,
            quantity=item.quantity,
            unit_price=item.unit_price,
            total=item.quantity * item.unit_price,
        )
        for item in purchase.items
    ]

    total_amount = sum(
        (item.total for item in items),
        start=Decimal(0),
    )

    return PurchaseRead(
        id=purchase.id,
        supplier_id=purchase.supplier_id,
        supplier_name=purchase.supplier.name,
        warehouse_id=purchase.warehouse_id,
        warehouse_name=purchase.warehouse.name,
        invoice_number=purchase.invoice_number,
        purchased_at=purchase.purchased_at,
        created_by_id=purchase.created_by_id,
        note=purchase.note,
        items=items,
        total_amount=total_amount,
    )


@router.post(
    "",
    response_model=PurchaseRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_purchase(
    data: PurchaseCreate,
    db: DBSessionDep,
    user: PurchaseManagerDep,
) -> PurchaseRead:
    service = PurchaseService(db)

    try:
        purchase = await service.create_purchase(
            data=data,
            created_by_id=user.id,
        )

    except SupplierNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Supplier not found",
        ) from exc

    except WarehouseNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Warehouse not found",
        ) from exc

    except ProductNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found",
        ) from exc

    except ProductCannotBePurchasedError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=("Only active raw materials and packaging can be purchased"),
        ) from exc

    except PurchaseAlreadyExistsError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Purchase invoice already exists",
        ) from exc

    except DuplicatePurchaseProductError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="A product cannot appear twice in one purchase",
        ) from exc

    return to_purchase_read(purchase)


@router.get(
    "/{purchase_id}",
    response_model=PurchaseRead,
)
async def get_purchase(
    purchase_id: int,
    db: DBSessionDep,
    _user: CurrentUserDep,
) -> PurchaseRead:
    service = PurchaseService(db)

    try:
        purchase = await service.get_purchase(purchase_id)

    except PurchaseNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Purchase not found",
        ) from exc

    return to_purchase_read(purchase)

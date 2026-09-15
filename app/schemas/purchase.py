from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field


class PurchaseItemCreate(BaseModel):
    product_id: int = Field(gt=0)

    quantity: Decimal = Field(gt=0)

    unit_price: Decimal = Field(ge=0)


class PurchaseCreate(BaseModel):
    supplier_id: int = Field(gt=0)

    warehouse_id: int = Field(gt=0)

    invoice_number: str | None = Field(
        default=None,
        max_length=100,
    )

    items: list[PurchaseItemCreate] = Field(
        min_length=1,
    )

    note: str | None = Field(
        default=None,
        max_length=500,
    )


class PurchaseItemRead(BaseModel):
    id: int
    product_id: int
    product_name: str

    quantity: Decimal
    unit_price: Decimal
    total: Decimal


class PurchaseRead(BaseModel):
    id: int

    supplier_id: int
    supplier_name: str

    warehouse_id: int
    warehouse_name: str

    invoice_number: str | None

    purchased_at: datetime
    created_by_id: int

    note: str | None

    items: list[PurchaseItemRead]

    total_amount: Decimal

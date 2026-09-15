from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field


class DeliveryItemCreate(BaseModel):
    product_id: int = Field(gt=0)
    quantity: Decimal = Field(gt=0)

    unit_price: Decimal | None = Field(
        default=None,
        ge=0,
    )


class DeliveryCreate(BaseModel):
    customer_id: int = Field(gt=0)
    warehouse_id: int = Field(gt=0)
    courier_id: int = Field(gt=0)

    items: list[DeliveryItemCreate] = Field(
        min_length=1,
    )

    note: str | None = Field(
        default=None,
        max_length=500,
    )


class DeliveryItemRead(BaseModel):
    id: int
    product_id: int
    product_name: str
    quantity: Decimal
    unit_price: Decimal
    total: Decimal


class DeliveryRead(BaseModel):
    id: int

    customer_id: int
    customer_name: str

    warehouse_id: int
    warehouse_name: str

    courier_id: int
    courier_name: str

    created_by_id: int

    delivered_at: datetime
    note: str | None

    items: list[DeliveryItemRead]
    total_amount: Decimal

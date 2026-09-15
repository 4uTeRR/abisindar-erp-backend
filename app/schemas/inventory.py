from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field


class WarehouseCreate(BaseModel):
    name: str = Field(
        min_length=2,
        max_length=100,
    )


class WarehouseRead(BaseModel):
    id: int
    name: str
    is_active: bool


class ProductionBatchCreate(BaseModel):
    product_id: int = Field(gt=0)

    warehouse_id: int = Field(gt=0)

    quantity: Decimal = Field(gt=0)

    package_count: int | None = Field(
        default=None,
        gt=0,
    )

    note: str | None = Field(
        default=None,
        max_length=500,
    )


class ProductionBatchRead(BaseModel):
    id: int
    product_id: int
    product_name: str

    warehouse_id: int
    warehouse_name: str

    quantity: Decimal
    package_count: int | None

    produced_at: datetime
    created_by_id: int

    note: str | None


class StockBalanceRead(BaseModel):
    product_id: int
    product_name: str

    warehouse_id: int
    warehouse_name: str

    quantity: Decimal

from decimal import Decimal

from pydantic import BaseModel, Field

from app.models.enums import ProductType


class UnitCreate(BaseModel):
    name: str = Field(
        min_length=1,
        max_length=50,
    )
    code: str = Field(
        min_length=1,
        max_length=20,
    )


class UnitRead(BaseModel):
    id: int
    name: str
    code: str


class CategoryCreate(BaseModel):
    name: str = Field(
        min_length=2,
        max_length=100,
    )
    description: str | None = Field(
        default=None,
        max_length=255,
    )


class CategoryRead(BaseModel):
    id: int
    name: str
    description: str | None


class ProductCreate(BaseModel):
    name: str = Field(
        min_length=2,
        max_length=150,
    )

    sku: str | None = Field(
        default=None,
        max_length=50,
    )

    product_type: ProductType

    base_unit_id: int = Field(gt=0)

    category_id: int = Field(gt=0)

    package_weight: Decimal | None = Field(
        default=None,
        gt=0,
    )

    sale_price: Decimal | None = Field(
        default=None,
        ge=0,
    )


class ProductRead(BaseModel):
    id: int
    name: str
    sku: str | None
    product_type: ProductType

    base_unit_id: int
    unit_name: str
    unit_code: str

    category_id: int
    category_name: str

    package_weight: Decimal | None
    sale_price: Decimal | None

    is_active: bool

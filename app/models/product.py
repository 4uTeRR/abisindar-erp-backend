from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Enum,
    ForeignKey,
    Numeric,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import ProductType

if TYPE_CHECKING:
    from app.models.category import Category
    from app.models.unit import Unit


class Product(Base):
    __tablename__ = "products"

    __table_args__ = (
        CheckConstraint(
            "sale_price IS NULL OR sale_price >= 0",
            name="ck_products_sale_price_non_negative",
        ),
        CheckConstraint(
            "package_weight IS NULL OR package_weight > 0",
            name="ck_products_package_weight_positive",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    name: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
        index=True,
    )

    sku: Mapped[str | None] = mapped_column(
        String(50),
        unique=True,
        nullable=True,
        index=True,
    )

    product_type: Mapped[ProductType] = mapped_column(
        Enum(
            ProductType,
            name="product_type",
            native_enum=False,
            length=30,
            create_constraint=True,
            values_callable=lambda enum_class: [item.value for item in enum_class],
        ),
        nullable=False,
    )

    base_unit_id: Mapped[int] = mapped_column(
        ForeignKey(
            "units.id",
            ondelete="RESTRICT",
        ),
        nullable=False,
        index=True,
    )

    category_id: Mapped[int] = mapped_column(
        ForeignKey(
            "categories.id",
            ondelete="RESTRICT",
        ),
        nullable=False,
        index=True,
    )

    package_weight: Mapped[Decimal | None] = mapped_column(
        Numeric(12, 3),
        nullable=True,
    )

    sale_price: Mapped[Decimal | None] = mapped_column(
        Numeric(15, 2),
        nullable=True,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    base_unit: Mapped[Unit] = relationship(
        back_populates="products",
    )

    category: Mapped[Category] = relationship(
        back_populates="products",
    )

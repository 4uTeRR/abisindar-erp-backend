from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import (
    CheckConstraint,
    ForeignKey,
    Numeric,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.delivery import Delivery
    from app.models.product import Product
    from app.models.stock_movement import StockMovement


class DeliveryItem(Base):
    __tablename__ = "delivery_items"

    __table_args__ = (
        CheckConstraint(
            "quantity > 0",
            name="ck_delivery_items_quantity_positive",
        ),
        CheckConstraint(
            "unit_price >= 0",
            name="ck_delivery_items_unit_price_non_negative",
        ),
        UniqueConstraint(
            "delivery_id",
            "product_id",
            name="uq_delivery_items_delivery_product",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    delivery_id: Mapped[int] = mapped_column(
        ForeignKey(
            "deliveries.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    product_id: Mapped[int] = mapped_column(
        ForeignKey(
            "products.id",
            ondelete="RESTRICT",
        ),
        nullable=False,
        index=True,
    )

    quantity: Mapped[Decimal] = mapped_column(
        Numeric(15, 3),
        nullable=False,
    )

    unit_price: Mapped[Decimal] = mapped_column(
        Numeric(15, 2),
        nullable=False,
    )

    delivery: Mapped[Delivery] = relationship(
        back_populates="items",
    )

    product: Mapped[Product] = relationship()

    stock_movements: Mapped[list[StockMovement]] = relationship(
        back_populates="delivery_item",
    )

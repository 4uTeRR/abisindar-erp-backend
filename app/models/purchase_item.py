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
    from app.models.product import Product
    from app.models.purchase import Purchase
    from app.models.stock_movement import StockMovement


class PurchaseItem(Base):
    __tablename__ = "purchase_items"

    __table_args__ = (
        CheckConstraint(
            "quantity > 0",
            name="ck_purchase_items_quantity_positive",
        ),
        CheckConstraint(
            "unit_price >= 0",
            name="ck_purchase_items_unit_price_non_negative",
        ),
        UniqueConstraint(
            "purchase_id",
            "product_id",
            name="uq_purchase_items_purchase_product",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    purchase_id: Mapped[int] = mapped_column(
        ForeignKey(
            "purchases.id",
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

    purchase: Mapped[Purchase] = relationship(
        back_populates="items",
    )

    product: Mapped[Product] = relationship()

    stock_movements: Mapped[list[StockMovement]] = relationship(
        back_populates="purchase_item",
    )

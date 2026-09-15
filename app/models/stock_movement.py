from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    Enum,
    ForeignKey,
    Numeric,
    String,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import StockMovementType

if TYPE_CHECKING:
    from app.models.delivery_item import DeliveryItem
    from app.models.product import Product
    from app.models.production_batch import ProductionBatch
    from app.models.purchase_item import PurchaseItem
    from app.models.user import User
    from app.models.warehouse import Warehouse


class StockMovement(Base):
    __tablename__ = "stock_movements"

    __table_args__ = (
        CheckConstraint(
            "quantity_delta <> 0",
            name="ck_stock_movements_quantity_delta_non_zero",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    product_id: Mapped[int] = mapped_column(
        ForeignKey(
            "products.id",
            ondelete="RESTRICT",
        ),
        nullable=False,
        index=True,
    )

    warehouse_id: Mapped[int] = mapped_column(
        ForeignKey(
            "warehouses.id",
            ondelete="RESTRICT",
        ),
        nullable=False,
        index=True,
    )

    movement_type: Mapped[StockMovementType] = mapped_column(
        Enum(
            StockMovementType,
            name="stock_movement_type",
            native_enum=False,
            length=30,
            create_constraint=True,
            values_callable=lambda enum_class: [item.value for item in enum_class],
        ),
        nullable=False,
    )

    quantity_delta: Mapped[Decimal] = mapped_column(
        Numeric(15, 3),
        nullable=False,
    )

    production_batch_id: Mapped[int | None] = mapped_column(
        ForeignKey(
            "production_batches.id",
            ondelete="RESTRICT",
        ),
        nullable=True,
        index=True,
    )

    created_by_id: Mapped[int] = mapped_column(
        ForeignKey(
            "users.id",
            ondelete="RESTRICT",
        ),
        nullable=False,
        index=True,
    )

    occurred_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    note: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    product: Mapped[Product] = relationship()

    warehouse: Mapped[Warehouse] = relationship(
        back_populates="stock_movements",
    )

    production_batch: Mapped[ProductionBatch | None] = relationship(
        back_populates="stock_movements",
    )

    created_by: Mapped[User] = relationship()

    delivery_item_id: Mapped[int | None] = mapped_column(
        ForeignKey(
            "delivery_items.id",
            name="fk_stock_movements_delivery_item_id_delivery_items",
            ondelete="RESTRICT",
        ),
        nullable=True,
        index=True,
    )

    delivery_item: Mapped[DeliveryItem | None] = relationship(
        back_populates="stock_movements",
    )

    purchase_item_id: Mapped[int | None] = mapped_column(
        ForeignKey(
            "purchase_items.id",
            name="fk_stock_movements_purchase_item_id_purchase_items",
            ondelete="RESTRICT",
        ),
        nullable=True,
        index=True,
    )

    purchase_item: Mapped[PurchaseItem | None] = relationship(
        back_populates="stock_movements",
    )

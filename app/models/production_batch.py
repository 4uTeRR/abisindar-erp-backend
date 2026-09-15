from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.product import Product
    from app.models.stock_movement import StockMovement
    from app.models.user import User
    from app.models.warehouse import Warehouse


class ProductionBatch(Base):
    __tablename__ = "production_batches"

    __table_args__ = (
        CheckConstraint(
            "quantity > 0",
            name="ck_production_batches_quantity_positive",
        ),
        CheckConstraint(
            "package_count IS NULL OR package_count > 0",
            name="ck_production_batches_package_count_positive",
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

    quantity: Mapped[Decimal] = mapped_column(
        Numeric(15, 3),
        nullable=False,
    )

    package_count: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    note: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    produced_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    created_by_id: Mapped[int] = mapped_column(
        ForeignKey(
            "users.id",
            ondelete="RESTRICT",
        ),
        nullable=False,
        index=True,
    )

    product: Mapped[Product] = relationship()

    warehouse: Mapped[Warehouse] = relationship(
        back_populates="production_batches",
    )

    created_by: Mapped[User] = relationship()

    stock_movements: Mapped[list[StockMovement]] = relationship(
        back_populates="production_batch",
    )

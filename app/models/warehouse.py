from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.production_batch import ProductionBatch
    from app.models.stock_movement import StockMovement


class Warehouse(Base):
    __tablename__ = "warehouses"

    id: Mapped[int] = mapped_column(primary_key=True)

    name: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    production_batches: Mapped[list[ProductionBatch]] = relationship(
        back_populates="warehouse",
    )

    stock_movements: Mapped[list[StockMovement]] = relationship(
        back_populates="warehouse",
    )

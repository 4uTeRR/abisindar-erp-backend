from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    DateTime,
    ForeignKey,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.purchase_item import PurchaseItem
    from app.models.supplier import Supplier
    from app.models.user import User
    from app.models.warehouse import Warehouse


class Purchase(Base):
    __tablename__ = "purchases"

    __table_args__ = (
        UniqueConstraint(
            "supplier_id",
            "invoice_number",
            name="uq_purchases_supplier_invoice_number",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    supplier_id: Mapped[int] = mapped_column(
        ForeignKey(
            "suppliers.id",
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

    invoice_number: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    purchased_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    note: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    created_by_id: Mapped[int] = mapped_column(
        ForeignKey(
            "users.id",
            ondelete="RESTRICT",
        ),
        nullable=False,
        index=True,
    )

    supplier: Mapped[Supplier] = relationship(
        back_populates="purchases",
    )

    warehouse: Mapped[Warehouse] = relationship()

    created_by: Mapped[User] = relationship()

    items: Mapped[list[PurchaseItem]] = relationship(
        back_populates="purchase",
        cascade="all, delete-orphan",
    )

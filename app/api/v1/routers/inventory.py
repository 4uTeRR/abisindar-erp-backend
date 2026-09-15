from fastapi import APIRouter, HTTPException, status

from app.api.deps import (
    AdminUserDep,
    CurrentUserDep,
    DBSessionDep,
    ProductionUserDep,
)
from app.core.exceptions import (
    ProductCannotBeProducedError,
    ProductNotFoundError,
    WarehouseAlreadyExistsError,
    WarehouseNotFoundError,
)
from app.schemas.inventory import (
    ProductionBatchCreate,
    ProductionBatchRead,
    StockBalanceRead,
    WarehouseCreate,
    WarehouseRead,
)
from app.services.inventory import InventoryService

router = APIRouter(
    prefix="/inventory",
    tags=["Inventory"],
)


@router.post(
    "/warehouses",
    response_model=WarehouseRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_warehouse(
    data: WarehouseCreate,
    db: DBSessionDep,
    _admin: AdminUserDep,
) -> WarehouseRead:
    service = InventoryService(db)

    try:
        warehouse = await service.create_warehouse(data)
    except WarehouseAlreadyExistsError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Warehouse already exists",
        ) from exc

    return WarehouseRead(
        id=warehouse.id,
        name=warehouse.name,
        is_active=warehouse.is_active,
    )


@router.get(
    "/warehouses",
    response_model=list[WarehouseRead],
)
async def get_warehouses(
    db: DBSessionDep,
    _user: CurrentUserDep,
) -> list[WarehouseRead]:
    service = InventoryService(db)

    warehouses = await service.get_warehouses()

    return [
        WarehouseRead(
            id=warehouse.id,
            name=warehouse.name,
            is_active=warehouse.is_active,
        )
        for warehouse in warehouses
    ]


@router.post(
    "/production",
    response_model=ProductionBatchRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_production(
    data: ProductionBatchCreate,
    db: DBSessionDep,
    user: ProductionUserDep,
) -> ProductionBatchRead:
    service = InventoryService(db)

    try:
        batch = await service.create_production_batch(
            data=data,
            user_id=user.id,
        )

    except ProductNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found",
        ) from exc

    except ProductCannotBeProducedError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Only active finished goods can be produced",
        ) from exc

    except WarehouseNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Warehouse not found",
        ) from exc

    return ProductionBatchRead(
        id=batch.id,
        product_id=batch.product_id,
        product_name=batch.product.name,
        warehouse_id=batch.warehouse_id,
        warehouse_name=batch.warehouse.name,
        quantity=batch.quantity,
        package_count=batch.package_count,
        produced_at=batch.produced_at,
        created_by_id=batch.created_by_id,
        note=batch.note,
    )


@router.get(
    "/stock/{product_id}",
    response_model=StockBalanceRead,
)
async def get_stock_balance(
    product_id: int,
    warehouse_id: int,
    db: DBSessionDep,
    _user: CurrentUserDep,
) -> StockBalanceRead:
    service = InventoryService(db)

    try:
        product, warehouse, quantity = await service.get_stock_balance(
            product_id=product_id,
            warehouse_id=warehouse_id,
        )

    except ProductNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found",
        ) from exc

    except WarehouseNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Warehouse not found",
        ) from exc

    return StockBalanceRead(
        product_id=product.id,
        product_name=product.name,
        warehouse_id=warehouse.id,
        warehouse_name=warehouse.name,
        quantity=quantity,
    )

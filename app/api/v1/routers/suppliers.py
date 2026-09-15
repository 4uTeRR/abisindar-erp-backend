from fastapi import APIRouter, HTTPException, Query, status

from app.api.deps import AdminUserDep, CurrentUserDep, DBSessionDep
from app.core.exceptions import SupplierAlreadyExistsError
from app.schemas.supplier import SupplierCreate, SupplierRead
from app.services.supplier import SupplierService

router = APIRouter(
    prefix="/suppliers",
    tags=["Suppliers"],
)


@router.post(
    "",
    response_model=SupplierRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_supplier(
    data: SupplierCreate,
    db: DBSessionDep,
    _admin: AdminUserDep,
) -> SupplierRead:
    service = SupplierService(db)

    try:
        supplier = await service.create_supplier(data)

    except SupplierAlreadyExistsError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Supplier with this code already exists",
        ) from exc

    return SupplierRead(
        id=supplier.id,
        name=supplier.name,
        code=supplier.code,
        phone=supplier.phone,
        address=supplier.address,
        is_active=supplier.is_active,
    )


@router.get(
    "",
    response_model=list[SupplierRead],
)
async def get_suppliers(
    db: DBSessionDep,
    _user: CurrentUserDep,
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=100),
) -> list[SupplierRead]:
    service = SupplierService(db)

    suppliers = await service.get_suppliers(
        offset=offset,
        limit=limit,
    )

    return [
        SupplierRead(
            id=supplier.id,
            name=supplier.name,
            code=supplier.code,
            phone=supplier.phone,
            address=supplier.address,
            is_active=supplier.is_active,
        )
        for supplier in suppliers
    ]

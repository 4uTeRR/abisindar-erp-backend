from fastapi import APIRouter, HTTPException, Query, status

from app.api.deps import AdminUserDep, CurrentUserDep, DBSessionDep
from app.core.exceptions import CustomerAlreadyExistsError
from app.schemas.customer import CustomerCreate, CustomerRead
from app.services.customer import CustomerService

router = APIRouter(
    prefix="/customers",
    tags=["Customers"],
)


@router.post(
    "",
    response_model=CustomerRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_customer(
    data: CustomerCreate,
    db: DBSessionDep,
    _admin: AdminUserDep,
) -> CustomerRead:
    service = CustomerService(db)

    try:
        customer = await service.create_customer(data)

    except CustomerAlreadyExistsError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Customer with this code already exists",
        ) from exc

    return CustomerRead(
        id=customer.id,
        name=customer.name,
        code=customer.code,
        phone=customer.phone,
        address=customer.address,
        is_active=customer.is_active,
    )


@router.get(
    "",
    response_model=list[CustomerRead],
)
async def get_customers(
    db: DBSessionDep,
    _user: CurrentUserDep,
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=100),
) -> list[CustomerRead]:
    service = CustomerService(db)

    customers = await service.get_customers(
        offset=offset,
        limit=limit,
    )

    return [
        CustomerRead(
            id=customer.id,
            name=customer.name,
            code=customer.code,
            phone=customer.phone,
            address=customer.address,
            is_active=customer.is_active,
        )
        for customer in customers
    ]

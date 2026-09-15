from fastapi import APIRouter, HTTPException, status

from app.api.deps import AdminUserDep, DBSessionDep
from app.core.exceptions import RoleAlreadyExistsError
from app.schemas.role import RoleCreate, RoleRead
from app.services.role import RoleService

router = APIRouter(
    prefix="/roles",
    tags=["Roles"],
)


@router.post(
    "",
    response_model=RoleRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_role(
    data: RoleCreate,
    db: DBSessionDep,
    _admin: AdminUserDep,
) -> RoleRead:
    service = RoleService(db)

    try:
        role = await service.create_role(data)
    except RoleAlreadyExistsError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Role already exists",
        ) from exc

    return RoleRead.model_validate(role)

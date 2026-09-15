from fastapi import APIRouter, HTTPException, Query, status

from app.api.deps import AdminUserDep, CurrentUserDep, DBSessionDep
from app.core.exceptions import (
    CannotDeactivateSelfError,
    RoleNotFoundError,
    UserAlreadyExistsError,
    UserNotFoundError,
)
from app.models.user import User
from app.schemas.user import (
    UserCreate,
    UserRead,
    UserStatusUpdate,
)
from app.services.user import UserService

router = APIRouter(
    prefix="/users",
    tags=["Users"],
)


def to_user_read(user: User) -> UserRead:
    return UserRead(
        id=user.id,
        full_name=user.full_name,
        email=user.email,
        is_active=user.is_active,
        role_name=user.role.name,
    )


@router.get(
    "/me",
    response_model=UserRead,
)
async def get_current_user_profile(
    current_user: CurrentUserDep,
) -> UserRead:
    return to_user_read(current_user)


@router.post(
    "",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_user(
    data: UserCreate,
    db: DBSessionDep,
    _admin: AdminUserDep,
) -> UserRead:
    service = UserService(db)

    try:
        user = await service.create_user(data)

    except UserAlreadyExistsError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with this email already exists",
        ) from exc

    except RoleNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found",
        ) from exc

    return to_user_read(user)


@router.get(
    "",
    response_model=list[UserRead],
)
async def get_users(
    db: DBSessionDep,
    _admin: AdminUserDep,
    offset: int = Query(
        default=0,
        ge=0,
    ),
    limit: int = Query(
        default=100,
        ge=1,
        le=100,
    ),
) -> list[UserRead]:
    service = UserService(db)

    users = await service.get_users(
        offset=offset,
        limit=limit,
    )

    return [to_user_read(user) for user in users]


@router.patch(
    "/{user_id}/status",
    response_model=UserRead,
)
async def update_user_status(
    user_id: int,
    data: UserStatusUpdate,
    db: DBSessionDep,
    admin: AdminUserDep,
) -> UserRead:
    service = UserService(db)

    try:
        user = await service.set_user_status(
            user_id=user_id,
            is_active=data.is_active,
            current_user_id=admin.id,
        )

    except UserNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        ) from exc

    except CannotDeactivateSelfError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="You cannot deactivate your own account",
        ) from exc

    return to_user_read(user)

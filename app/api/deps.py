from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import InvalidTokenError
from app.core.security import decode_access_token
from app.db.session import get_db
from app.models.user import User
from app.repositories.user import UserRepository

DBSessionDep = Annotated[AsyncSession, Depends(get_db)]

bearer_scheme = HTTPBearer(
    auto_error=False,
)

BearerCredentialsDep = Annotated[
    HTTPAuthorizationCredentials | None,
    Depends(bearer_scheme),
]


async def get_current_user(
    db: DBSessionDep,
    credentials: BearerCredentialsDep,
) -> User:
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if credentials.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication scheme",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        user_id = decode_access_token(
            credentials.credentials,
        )
    except InvalidTokenError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired access token",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc

    repository = UserRepository(db)

    user = await repository.get_by_id(user_id)

    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User is unavailable",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


CurrentUserDep = Annotated[
    User,
    Depends(get_current_user),
]


async def require_admin(
    current_user: CurrentUserDep,
) -> User:
    if current_user.role.name != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Administrator access required",
        )

    return current_user


AdminUserDep = Annotated[
    User,
    Depends(require_admin),
]


async def require_production_user(
    current_user: CurrentUserDep,
) -> User:
    allowed_roles = {
        "admin",
        "operator",
    }

    if current_user.role.name not in allowed_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Production access required",
        )

    return current_user


ProductionUserDep = Annotated[
    User,
    Depends(require_production_user),
]


async def require_delivery_manager(
    current_user: CurrentUserDep,
) -> User:
    allowed_roles = {
        "admin",
        "operator",
    }

    if current_user.role.name not in allowed_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Delivery management access required",
        )

    return current_user


DeliveryManagerDep = Annotated[
    User,
    Depends(require_delivery_manager),
]


async def require_purchase_manager(
    current_user: CurrentUserDep,
) -> User:
    allowed_roles = {
        "admin",
        "operator",
    }

    if current_user.role.name not in allowed_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Purchase management access required",
        )

    return current_user


PurchaseManagerDep = Annotated[
    User,
    Depends(require_purchase_manager),
]

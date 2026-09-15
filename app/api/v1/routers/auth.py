from fastapi import APIRouter, HTTPException, status

from app.api.deps import DBSessionDep
from app.core.exceptions import InvalidCredentialsError
from app.schemas.auth import LoginRequest, TokenResponse
from app.services.auth import AuthService

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


@router.post(
    "/login",
    response_model=TokenResponse,
)
async def login(
    data: LoginRequest,
    db: DBSessionDep,
) -> TokenResponse:
    service = AuthService(db)

    try:
        token = await service.login(data)
    except InvalidCredentialsError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        ) from exc

    return TokenResponse(
        access_token=token,
    )

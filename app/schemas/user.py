from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    full_name: str = Field(
        min_length=2,
        max_length=150,
    )

    email: EmailStr

    password: str = Field(
        min_length=8,
        max_length=128,
    )

    role_name: str = Field(
        min_length=2,
        max_length=50,
    )


class UserStatusUpdate(BaseModel):
    is_active: bool


class UserRead(BaseModel):
    id: int
    full_name: str
    email: EmailStr
    is_active: bool
    role_name: str

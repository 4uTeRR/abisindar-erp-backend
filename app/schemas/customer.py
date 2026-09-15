from pydantic import BaseModel, Field


class CustomerCreate(BaseModel):
    name: str = Field(
        min_length=2,
        max_length=150,
    )

    code: str | None = Field(
        default=None,
        max_length=50,
    )

    phone: str | None = Field(
        default=None,
        max_length=50,
    )

    address: str | None = Field(
        default=None,
        max_length=255,
    )


class CustomerRead(BaseModel):
    id: int
    name: str
    code: str | None
    phone: str | None
    address: str | None
    is_active: bool

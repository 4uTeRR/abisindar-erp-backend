from pydantic import BaseModel, ConfigDict, Field


class RoleCreate(BaseModel):
    name: str = Field(
        min_length=2,
        max_length=50,
    )
    description: str | None = Field(
        default=None,
        max_length=255,
    )


class RoleRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str | None

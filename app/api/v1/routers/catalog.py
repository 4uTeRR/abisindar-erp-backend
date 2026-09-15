from fastapi import APIRouter, HTTPException, Query, status

from app.api.deps import AdminUserDep, CurrentUserDep, DBSessionDep
from app.core.exceptions import (
    CategoryAlreadyExistsError,
    CategoryNotFoundError,
    ProductAlreadyExistsError,
    UnitAlreadyExistsError,
    UnitNotFoundError,
)
from app.models.product import Product
from app.schemas.catalog import (
    CategoryCreate,
    CategoryRead,
    ProductCreate,
    ProductRead,
    UnitCreate,
    UnitRead,
)
from app.services.catalog import CatalogService

router = APIRouter(
    prefix="/catalog",
    tags=["Catalog"],
)


def to_product_read(product: Product) -> ProductRead:
    return ProductRead(
        id=product.id,
        name=product.name,
        sku=product.sku,
        product_type=product.product_type,
        base_unit_id=product.base_unit_id,
        unit_name=product.base_unit.name,
        unit_code=product.base_unit.code,
        category_id=product.category_id,
        category_name=product.category.name,
        package_weight=product.package_weight,
        sale_price=product.sale_price,
        is_active=product.is_active,
    )


@router.post(
    "/units",
    response_model=UnitRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_unit(
    data: UnitCreate,
    db: DBSessionDep,
    _admin: AdminUserDep,
) -> UnitRead:
    service = CatalogService(db)

    try:
        unit = await service.create_unit(data)

    except UnitAlreadyExistsError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Unit already exists",
        ) from exc

    return UnitRead(
        id=unit.id,
        name=unit.name,
        code=unit.code,
    )


@router.get(
    "/units",
    response_model=list[UnitRead],
)
async def get_units(
    db: DBSessionDep,
    _user: CurrentUserDep,
) -> list[UnitRead]:
    service = CatalogService(db)

    units = await service.get_units()

    return [
        UnitRead(
            id=unit.id,
            name=unit.name,
            code=unit.code,
        )
        for unit in units
    ]


@router.post(
    "/categories",
    response_model=CategoryRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_category(
    data: CategoryCreate,
    db: DBSessionDep,
    _admin: AdminUserDep,
) -> CategoryRead:
    service = CatalogService(db)

    try:
        category = await service.create_category(data)

    except CategoryAlreadyExistsError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Category already exists",
        ) from exc

    return CategoryRead(
        id=category.id,
        name=category.name,
        description=category.description,
    )


@router.get(
    "/categories",
    response_model=list[CategoryRead],
)
async def get_categories(
    db: DBSessionDep,
    _user: CurrentUserDep,
) -> list[CategoryRead]:
    service = CatalogService(db)

    categories = await service.get_categories()

    return [
        CategoryRead(
            id=category.id,
            name=category.name,
            description=category.description,
        )
        for category in categories
    ]


@router.post(
    "/products",
    response_model=ProductRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_product(
    data: ProductCreate,
    db: DBSessionDep,
    _admin: AdminUserDep,
) -> ProductRead:
    service = CatalogService(db)

    try:
        product = await service.create_product(data)

    except UnitNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Unit not found",
        ) from exc

    except CategoryNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found",
        ) from exc

    except ProductAlreadyExistsError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Product already exists",
        ) from exc

    return to_product_read(product)


@router.get(
    "/products",
    response_model=list[ProductRead],
)
async def get_products(
    db: DBSessionDep,
    _user: CurrentUserDep,
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=100),
) -> list[ProductRead]:
    service = CatalogService(db)

    products = await service.get_products(
        offset=offset,
        limit=limit,
    )

    return [to_product_read(product) for product in products]

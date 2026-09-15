from fastapi import APIRouter

from app.api.v1.routers.auth import router as auth_router
from app.api.v1.routers.catalog import router as catalog_router
from app.api.v1.routers.customers import router as customers_router
from app.api.v1.routers.deliveries import router as deliveries_router
from app.api.v1.routers.inventory import router as inventory_router
from app.api.v1.routers.purchases import router as purchases_router
from app.api.v1.routers.roles import router as roles_router
from app.api.v1.routers.suppliers import router as suppliers_router
from app.api.v1.routers.users import router as users_router

api_router = APIRouter()

api_router.include_router(auth_router)
api_router.include_router(roles_router)
api_router.include_router(users_router)
api_router.include_router(catalog_router)
api_router.include_router(inventory_router)
api_router.include_router(customers_router)
api_router.include_router(deliveries_router)
api_router.include_router(suppliers_router)
api_router.include_router(purchases_router)

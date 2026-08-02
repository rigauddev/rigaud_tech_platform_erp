from fastapi import APIRouter

from app.api.v1.routes import health
from app.modules.audit.presentation.router import router as audit_router
from app.modules.auth.presentation.router import router as auth_router
from app.modules.categories.presentation.router import router as categories_router
from app.modules.companies.presentation.router import router as companies_router
from app.modules.inventory.presentation.router import router as inventory_router
from app.modules.inventory.presentation.warehouse_router import router as warehouses_router
from app.modules.products.presentation.router import router as products_router
from app.modules.users.presentation.router import router as users_router
from app.shared.demo.router import router as demo_router

api_router = APIRouter()
api_router.include_router(audit_router)
api_router.include_router(auth_router)
api_router.include_router(categories_router)
api_router.include_router(companies_router)
api_router.include_router(inventory_router)
api_router.include_router(warehouses_router)
api_router.include_router(products_router)
api_router.include_router(users_router)
api_router.include_router(demo_router)
api_router.include_router(health.router, prefix="/health", tags=["Health"])

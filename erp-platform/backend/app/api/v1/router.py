from fastapi import APIRouter

from app.api.v1.routes import health
from app.modules.audit.presentation.router import router as audit_router
from app.modules.auth.presentation.router import router as auth_router
from app.modules.billing.presentation.router import router as billing_router
from app.modules.companies.presentation.router import router as companies_router
from app.modules.entitlements.presentation.router import router as entitlements_router
from app.modules.feature_flags.presentation.router import router as feature_flags_router
from app.modules.plan.presentation.router import router as plans_router
from app.modules.products.presentation.router import router as products_router
from app.modules.subscription.presentation.router import router as subscriptions_router
from app.modules.users.presentation.router import router as users_router

api_router = APIRouter()
api_router.include_router(audit_router)
api_router.include_router(auth_router)
api_router.include_router(companies_router)
api_router.include_router(plans_router)
api_router.include_router(subscriptions_router)
api_router.include_router(entitlements_router)
api_router.include_router(feature_flags_router)
api_router.include_router(billing_router)
api_router.include_router(products_router)
api_router.include_router(users_router)
api_router.include_router(health.router, prefix="/health", tags=["Health"])

from fastapi import APIRouter
from twinpay_tr.api.v1 import users, payments, sandbox, webhooks, settings

api_router = APIRouter()
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(payments.router, prefix="/payments", tags=["payments"])
api_router.include_router(webhooks.router, prefix="/webhooks", tags=["webhooks"])
api_router.include_router(settings.router, prefix="/settings", tags=["settings"])
api_router.include_router(sandbox.router, prefix="/sandbox", tags=["sandbox"])

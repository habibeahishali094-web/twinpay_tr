import os
import hashlib
import time
from fastapi import FastAPI, Request
from starlette.middleware.base import BaseHTTPMiddleware
from twinpay_tr.api.v1.router import api_router
from twinpay_tr.core.config import settings
from twinpay_tr.db.base import Base
from twinpay_tr.db.session import engine, SessionLocal

# Import models
from twinpay_tr.models.user import User
from twinpay_tr.models.payment import Payment
from twinpay_tr.models.webhook import WebhookEndpoint
from twinpay_tr.models.idempotency import IdempotencyKey
from twinpay_tr.models.settings import Settings
from twinpay_tr.models.scenario import Scenario
from twinpay_tr.models.log import RequestLog

from twinpay_tr.web.router import router as web_router

Base.metadata.create_all(bind=engine)

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        if request.url.path.startswith("/api/") and not os.getenv("TESTING"):
            db = SessionLocal()
            try:
                auth = request.headers.get("Authorization")
                user_id = None
                if auth and auth.startswith("Bearer "):
                    token = auth.replace("Bearer ", "")
                    prefix = token[:8]
                    from twinpay_tr.core.security import verify_api_key
                    user = db.query(User).filter(User.api_key_prefix == prefix).first()
                    if user and verify_api_key(token, user.api_key_hash):
                        user_id = user.id
                
                if user_id:
                    log = RequestLog(
                        user_id=user_id,
                        method=request.method,
                        path=request.url.path,
                        status_code=response.status_code
                    )
                    db.add(log)
                    db.commit()
            except Exception:
                pass
            finally:
                db.close()
                
        return response

app = FastAPI(title=settings.PROJECT_NAME)

app.add_middleware(RequestLoggingMiddleware)

app.include_router(api_router, prefix=settings.API_V1_STR)
app.include_router(web_router)

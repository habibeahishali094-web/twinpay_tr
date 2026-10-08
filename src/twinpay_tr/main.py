from fastapi import FastAPI
from twinpay_tr.api.v1.router import api_router
from twinpay_tr.core.config import settings
from twinpay_tr.db.base import Base
from twinpay_tr.db.session import engine
from twinpay_tr.models import User

Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.PROJECT_NAME)

app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/")
def root():
    return {"message": "TwinPay TR API'sine Hoş Geldiniz. Lütfen dokümantasyon için /docs adresine gidin."}

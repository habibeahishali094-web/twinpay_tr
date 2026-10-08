import hashlib
from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from twinpay_tr.api.deps import get_db
from twinpay_tr.models.user import User
from twinpay_tr.models.payment import Payment
from twinpay_tr.models.settings import Settings
from twinpay_tr.models.log import RequestLog
from twinpay_tr.api.v1.settings import get_or_create_settings

router = APIRouter()
templates = Jinja2Templates(directory="src/twinpay_tr/templates")

def get_user_from_cookie(request: Request, db: Session):
    api_key = request.cookies.get("api_key")
    if not api_key:
        return None
    token_hash = hashlib.sha256(api_key.encode()).hexdigest()
    return db.query(User).filter(User.api_key_hash == token_hash).first()

@router.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@router.post("/login")
def login(request: Request, api_key: str = Form(...), db: Session = Depends(get_db)):
    token_hash = hashlib.sha256(api_key.encode()).hexdigest()
    user = db.query(User).filter(User.api_key_hash == token_hash).first()
    if not user:
        return templates.TemplateResponse("login.html", {"request": request, "error": "Geçersiz API Anahtarı"})
        
    response = RedirectResponse(url="/dashboard", status_code=302)
    response.set_cookie(key="api_key", value=api_key)
    return response

@router.get("/logout")
def logout(request: Request):
    response = RedirectResponse(url="/", status_code=302)
    response.delete_cookie("api_key")
    return response

@router.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request, db: Session = Depends(get_db)):
    user = get_user_from_cookie(request, db)
    if not user:
        return RedirectResponse(url="/")
        
    payments = db.query(Payment).filter(Payment.user_id == user.id).order_by(Payment.created_at.desc()).limit(20).all()
    settings = get_or_create_settings(db, user.id)
    
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "user": user,
        "payments": payments,
        "settings": settings
    })

@router.get("/logs", response_class=HTMLResponse)
def logs(request: Request, db: Session = Depends(get_db)):
    user = get_user_from_cookie(request, db)
    if not user:
        return RedirectResponse(url="/")
        
    logs = db.query(RequestLog).filter(RequestLog.user_id == user.id).order_by(RequestLog.created_at.desc()).limit(50).all()
    
    return templates.TemplateResponse("logs.html", {
        "request": request,
        "user": user,
        "logs": logs
    })

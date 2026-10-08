from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from twinpay_tr.api import deps
from twinpay_tr.models.user import User
from twinpay_tr.schemas.user import UserCreate, UserCreateResponse, UserResponse
from twinpay_tr.core.security import generate_api_key

router = APIRouter()

@router.post("/register", response_model=UserCreateResponse, status_code=status.HTTP_201_CREATED)
def register_user(user_in: UserCreate, db: Session = Depends(deps.get_db)):
    existing_user = db.query(User).filter(User.username == user_in.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Kullanıcı adı zaten alınmış.")
    
    api_key, prefix, hashed_key = generate_api_key()
    
    new_user = User(
        username=user_in.username,
        api_key_prefix=prefix,
        api_key_hash=hashed_key
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return UserCreateResponse(
        id=new_user.id,
        username=new_user.username,
        api_key_prefix=new_user.api_key_prefix,
        api_key=api_key
    )

@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(deps.get_current_user)):
    return current_user

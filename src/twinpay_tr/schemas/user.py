from pydantic import BaseModel

class UserCreate(BaseModel):
    username: str

class UserResponse(BaseModel):
    id: int
    username: str
    api_key_prefix: str

class UserCreateResponse(UserResponse):
    api_key: str # Sadece kayıtta bir kez dönecek

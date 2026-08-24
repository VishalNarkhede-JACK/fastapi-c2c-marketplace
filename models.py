from pydantic import BaseModel, EmailStr
from datetime import datetime

class Produk(BaseModel):
    id: int | None = None #for getting the id Automatically
    name: str
    description: str
    price: float
    quantity: int

# the user login and password section(addtion to the base code)
class UserCreate(BaseModel):
    email: EmailStr
    password: str

class ResponseToUser(BaseModel):
    email : EmailStr
    created_at : datetime
    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class CartItemAdd(BaseModel):
    product_id: int
    quantity: int = 1  # Defaults to 1 if the user doesn't specify
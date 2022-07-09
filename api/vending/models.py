from typing import List, Optional
from pydantic import BaseModel, validator

from vending.utils import validate_values


class ProductBase(BaseModel):
    product_name: str
    amount_available: int
    cost: int

    @validator("amount_available")
    def validate_amount(cls, v):
        if v < 0:
            raise ValueError("Amount can't be negative number")
        return v

    @validator("cost")
    def validate_cost(cls, v):
        return validate_values(v, "cost")


class ProductCreate(ProductBase):
    pass


class Product(ProductBase):
    id: int
    seller_id: int

    class Config:
        orm_mode = True


class UserBase(BaseModel):
    username: str
    role: str

    @validator("username")
    def validate_username(cls, v):
        if len(v) < 4:
            raise ValueError("Username must be at least 4 chars long")
        return v

    @validator("role")
    def validate_role(cls, v):
        if v not in ["buyer", "seller"]:
            raise ValueError("Incorrect role. Must be either buyer or seller.")
        return v


class UserCreate(UserBase):
    password: str

    @validator("password")
    def validate_password(cls, v):
        if len(v) < 6:
            raise ValueError("Password must be at least 6 chars long")
        return v


class User(UserBase):
    id: int
    deposit: int
    products: list[Product] = []
    access_token: Optional[str]
    token_type: Optional[str]

    class Config:
        orm_mode = True


class DepositRequest(BaseModel):
    amount: int

    @validator("amount")
    def validate_cost(cls, v):
        if v < 0:
            raise ValueError("Amount can't be negative number")
        elif v not in [5, 10, 20, 50, 100]:
            raise ValueError("You can only deposit 5,10,20,50 or 100")
        return v


class BuyRequest(BaseModel):
    product_name: str
    amount: int

    @validator("amount")
    def validate_cost(cls, v):
        if v < 0:
            raise ValueError("Amount can't be negative number")
        return v


class BuyResponse(BaseModel):
    total_spent: int
    products: List[str]
    amount: int
    change: int


class TokenData(BaseModel):
    username: Optional[str] = None

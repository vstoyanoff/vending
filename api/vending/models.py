from typing import List, Optional
from pydantic import BaseModel, validator

from vending.utils import validate_values


class Product(BaseModel):
    amount_available: int
    cost: int
    product_name: str

    @validator("amount_available")
    def validate_amount(cls, v):
        if v < 0:
            raise ValueError("Amount can't be negative number")
        return v

    @validator("cost")
    def validate_cost(cls, v):
        return validate_values(v, "cost")


class DBProduct(Product):
    id: str
    seller_id: str


class User(BaseModel):
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


class DBUser(User):
    id: str
    deposit: int
    token: str


class RegisterUser(User):
    password: str

    @validator("password")
    def validate_password(cls, v):
        if len(v) < 6:
            raise ValueError("Password must be at least 6 chars long")
        return v


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


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None

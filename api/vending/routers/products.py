from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from vending.db import actions, get_db
from vending.models import BuyRequest, BuyResponse, User, Product, ProductCreate
from vending.routers.auth import authorize_user

router = APIRouter()


@router.get("/products", response_model=List[Product], tags=["products"])
def get_products(db: Session = Depends(get_db), _=Depends(authorize_user)):
    return actions.get_products(db)


@router.get("/products/{product_name}", response_model=Product, tags=["products"])
def get_product(
    product_name: str, _=Depends(authorize_user), db: Session = Depends(get_db)
):
    product = actions.get_product(db, product_name)

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No such product",
        )

    return product


@router.post("/products", response_model=Product, tags=["products"])
def create_product(
    new_product: ProductCreate,
    user: User = Depends(authorize_user),
    db: Session = Depends(get_db),
):
    if user.role != "seller":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You need to be a seller to create products",
        )

    db_product = actions.get_product(db, new_product.product_name)

    if db_product:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="There is a product with the same name.",
        )

    product = actions.create_product(db, new_product, user)

    return product


@router.put("/products/{product_name}", response_model=Product, tags=["products"])
def update_product(
    product_name: str,
    updated_product_data: ProductCreate,
    user: User = Depends(authorize_user),
    db: Session = Depends(get_db),
):
    product = actions.get_product(db, product_name)

    if product.seller_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You are not authorized to perform this operation",
        )

    updated_product = actions.update_product(db, updated_product_data)

    return updated_product


@router.delete("/products/{product_name}", response_model=bool, tags=["products"])
def delete_product(
    product_name: str,
    user: User = Depends(authorize_user),
    db: Session = Depends(get_db),
):
    db_product = actions.get_product(db, product_name)

    if user.id != db_product.seller_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You are not authorized to perform this operation",
        )

    actions.delete_product(db, db_product.id)

    return True


@router.post("/buy", response_model=BuyResponse, tags=["products"])
def buy(
    buy_request: BuyRequest,
    user: User = Depends(authorize_user),
    db: Session = Depends(get_db),
):
    if user.role != "buyer":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You must be a buyer in order to buy things and deposit coins",
        )

    product = actions.get_product(db, buy_request.product_name)

    if buy_request.amount > product.amount_available:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="There is not enough units of this product.",
        )

    amount_to_pay = buy_request.amount * product.cost

    if amount_to_pay > user.deposit:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You don't have enough coins to for this order.",
        )

    change = user.deposit - amount_to_pay
    new_amount = product.amount_available - buy_request.amount

    actions.deposit(db, user.username, change)

    product_data = ProductCreate(
        product_name=product.product_name,
        cost=product.cost,
        amount_available=new_amount,
    )
    actions.update_product(db, product_data)

    return BuyResponse(
        total_spent=amount_to_pay,
        products=[product.product_name],
        amount=buy_request.amount,
        change=change,
    )

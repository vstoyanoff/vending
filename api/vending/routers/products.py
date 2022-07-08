from typing import List

from fastapi import APIRouter, Depends, HTTPException, status

from vending.db import actions
from vending.models import BuyRequest, BuyResponse, DBUser, DBProduct, User, Product
from vending.routers.auth import authorize_user

router = APIRouter()


@router.get("/products", response_model=List[DBProduct], tags=["products"])
def get_products(_=Depends(authorize_user)):
    return actions.get_products()


@router.get("/products/{product_name}", response_model=DBProduct, tags=["products"])
def get_product(product_name: str, _=Depends(authorize_user)):
    product = actions.get_product(product_name)

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No such product",
        )

    return product


@router.post("/products", response_model=DBProduct, tags=["products"])
def create_product(new_product: Product, user: User = Depends(authorize_user)):
    if user.role != "seller":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You need to be a seller to create products",
        )

    db_product = actions.get_product(new_product.product_name)

    if db_product:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="There is a product with the same name.",
        )

    actions.create_product(new_product, user)

    product = actions.get_product(new_product.product_name)

    return product


@router.put("/products/{product_name}", response_model=DBProduct, tags=["products"])
def update_product(
    product_name: str,
    updated_product_data: Product,
    user: User = Depends(authorize_user),
):
    product = actions.get_product(product_name)

    if product.seller_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You are not authorized to perform this operation",
        )

    params = product.dict()
    params.update(updated_product_data.dict())
    updated_product = DBProduct(**params)

    actions.update_product(updated_product)

    return updated_product


@router.delete("/products/{product_name}", response_model=bool, tags=["products"])
def delete_product(product_name: str, user: User = Depends(authorize_user)):
    db_product = actions.get_product(product_name)

    if user.id != db_product.seller_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You are not authorized to perform this operation",
        )

    actions.delete_product(db_product.id)

    return True


@router.post("/buy", response_model=BuyResponse, tags=["products"])
def buy(buy_request: BuyRequest, user: DBUser = Depends(authorize_user)):
    if user.role != "buyer":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You must be a buyer in order to buy things and deposit coins",
        )

    product = actions.get_product(buy_request.product_name)

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

    updated_user = DBUser(**user.dict(exclude={"deposit"}), deposit=change)
    actions.deposit(updated_user)

    updated_product = DBProduct(
        **product.dict(exclude={"amount_available"}), amount_available=new_amount
    )
    actions.update_product(updated_product)

    return BuyResponse(
        total_spent=amount_to_pay,
        products=[product.product_name],
        amount=buy_request.amount,
        change=change,
    )

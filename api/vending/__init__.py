from datetime import timedelta
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm

from vending.auth import (
    ACCESS_TOKEN_EXPIRE_DAYS,
    authorize_user,
    create_access_token,
    hash_password,
    verify_password,
)
from vending.db import actions, setup as db_setup
from vending.models import BuyRequest, BuyOperation, DBUser, DBProduct, User, Product
from vending.utils import validate_values

db_setup()
app = FastAPI()

origins = ["http://localhost", "http://localhost:8000"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/token")
def token(user: DBUser = Depends(authorize_user)):
    return user.dict(exclude={"password"})


@app.post("/login", response_model=DBUser)
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = actions.get_user(form_data.username)
    incorrect_credentials = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect username or password",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if not user:
        raise incorrect_credentials

    hashed_password = hash_password(form_data.password)
    if not verify_password(form_data.password, hashed_password):
        raise incorrect_credentials

    access_token_expires = timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )

    user = DBUser(**user.dict(exclude={"token"}), token=access_token)

    return user.dict(exclude={"password"})


@app.get("/users/{username}")
def get_user(username: str, _=Depends(authorize_user)):
    user = actions.get_user(username)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No such user",
        )

    return user.dict(exclude={"password"})


@app.post("/users")
def create_user(user: User):
    password_hash = hash_password(user.password)
    user = User(username=user.username, password=password_hash, role=user.role)
    db_user = actions.get_user(user.username)

    if db_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="User already exists"
        )

    actions.create_user(user)

    access_token_expires = timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )

    user = User(**user.dict(exclude={"token"}), token=access_token)

    return user.dict(exclude={"password"})


@app.post("/deposit")
def deposit(data: dict, user: DBUser = Depends(authorize_user)):
    if user.role != "buyer":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You must be a buyer in order to buy things and deposit coins",
        )

    try:
        amount = validate_values(data["amount"], "deposit")
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    if amount > 100:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Can't deposit more than 100",
        )

    deposit = user.deposit + amount

    updated_user = DBUser(
        id=user.id,
        username=user.username,
        password=user.password,
        deposit=deposit,
        role=user.role,
    )

    actions.deposit(updated_user)

    return {"completed": True}


@app.get("/products")
def get_products(_=Depends(authorize_user)):
    return actions.get_products()


@app.get("/products/{product_name}")
def get_product(product_name: str, _=Depends(authorize_user)):
    product = actions.get_product(product_name)

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No such product",
        )

    return product


@app.post("/products")
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


@app.put("/products/{product_name}")
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

    return {"completed": True}


@app.delete("/products/{product_name}")
def delete_product(product_name: str, user: User = Depends(authorize_user)):
    db_product = actions.get_product(product_name)

    if user.id != db_product.seller_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You are not authorized to perform this operation",
        )

    actions.delete_product(db_product.id)

    return {"completed": True}


@app.post("/buy")
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

    return BuyOperation(
        total_spent=amount_to_pay,
        products=[product.product_name],
        amount=buy_request.amount,
        change=change,
    )


@app.get("/reset")
def reset(user: DBUser = Depends(authorize_user)):
    updated_user = DBUser(**user.dict(exclude={"deposit"}), deposit=0)
    actions.deposit(updated_user)

    return {"completed": True}

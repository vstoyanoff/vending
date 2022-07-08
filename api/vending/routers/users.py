from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status

from vending.db import actions
from vending.models import DBUser, User
from vending.utils import validate_values
from vending.routers.auth import (
    authorize_user,
    create_access_token,
    hash_password,
)
from vending.settings import ACCESS_TOKEN_EXPIRE_DAYS

router = APIRouter()


@router.get("/users/{username}", tags=["users"])
def get_user(username: str, _=Depends(authorize_user)):
    user = actions.get_user(username)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No such user",
        )

    return user.dict(exclude={"password"})


@router.post("/users", tags=["users"])
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


@router.post("/deposit", tags=["users"])
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


@router.get("/reset", tags=["users"])
def reset(user: DBUser = Depends(authorize_user)):
    updated_user = DBUser(**user.dict(exclude={"deposit"}), deposit=0)
    actions.deposit(updated_user)

    return {"completed": True}

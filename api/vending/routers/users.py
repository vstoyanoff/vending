from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from vending.db import actions, get_db
from vending.models import User, UserCreate, DepositRequest
from vending.routers.auth import (
    authorize_user,
    create_access_token,
    hash_password,
)
from vending.settings import ACCESS_TOKEN_EXPIRE_DAYS, TOKEN_TYPE

router = APIRouter()


@router.get("/users/{username}", response_model=User, tags=["users"])
def get_user(username: str, db: Session = Depends(get_db), _=Depends(authorize_user)):
    user = actions.get_user(db, username)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No such user",
        )

    return user


@router.post("/users", response_model=User, tags=["users"])
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = actions.get_user(db, user.username)

    if db_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="User already exists"
        )

    password_hash = hash_password(user.password)
    user = UserCreate(username=user.username, password=password_hash, role=user.role)

    user = actions.create_user(db, user)
    access_token_expires = timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )

    user.access_token = access_token
    user.token_type = TOKEN_TYPE

    return user


@router.post("/deposit", response_model=User, tags=["users"])
def deposit(
    data: DepositRequest,
    user: User = Depends(authorize_user),
    db: Session = Depends(get_db),
):
    if user.role != "buyer":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You must be a buyer in order to buy things and deposit coins",
        )

    amount = user.deposit + data.amount
    user = actions.deposit(db, user.username, amount)

    return user


@router.get("/reset", response_model=User, tags=["users"])
def reset(user: User = Depends(authorize_user), db: Session = Depends(get_db)):
    return actions.deposit(db, user.username, 0)

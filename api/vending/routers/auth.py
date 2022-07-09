from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt, JWTError
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from vending.db import actions, get_db
from vending.models import User, TokenData
from vending.settings import ACCESS_TOKEN_EXPIRE_DAYS, ALGORITHM, SECRET_KEY, TOKEN_TYPE

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

router = APIRouter()

# Utils


def _decode_token(token: str) -> str:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            return None
        token_data = TokenData(username=username)
    except JWTError:
        return None
    return token_data.username


def _verify_password(plain_password: str, hashed_password: str) -> str:
    return pwd_context.verify(plain_password, hashed_password)


def authorize_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials. Your token might have been expired. Please login again.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    username = _decode_token(token)

    if username is None:
        raise credentials_exception

    user = actions.get_user(db, username)
    if not user:
        raise credentials_exception

    user.access_token = token
    user.token_type = TOKEN_TYPE

    return user


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=5)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt


# Routes


@router.get("/me", response_model=User, tags=["auth"])
def token(user: User = Depends(authorize_user)):
    return user


@router.post("/login", response_model=User, tags=["auth"])
def login(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    user = actions.get_user(db, form_data.username)
    incorrect_credentials = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect username or password",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if not user:
        raise incorrect_credentials

    db_password = actions.get_user_password(db, user.username)
    if not _verify_password(form_data.password, db_password):
        raise incorrect_credentials

    access_token_expires = timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )

    user.access_token = access_token
    user.token_type = TOKEN_TYPE

    return user

import os

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

db = "vending.sql"
engine = None
session = None

Base = declarative_base()


def _db_name(db_name: str = ""):
    global db

    if not db_name:
        return db

    db = db_name
    return db


def get_engine():
    global engine

    if not engine:
        db_name = _db_name()
        engine = create_engine(
            f"sqlite:///./{db_name}", connect_args={"check_same_thread": False}
        )

    return engine


def get_session():
    global session

    engine = get_engine()

    if not session:
        session = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    return session


def get_db():
    session = get_session()
    db = session()
    try:
        return db
    finally:
        db.close()


def setup(db: str = ""):
    db_name = _db_name(db)

    if not os.path.exists(f"./{db_name}"):
        from vending.orm import users
        from vending.orm import products

        engine = get_engine()
        users.Base.metadata.create_all(bind=engine)
        products.Base.metadata.create_all(bind=engine)

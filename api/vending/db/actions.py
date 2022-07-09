from sqlalchemy.orm import Session

from vending import models
from vending.orm.users import User
from vending.orm.products import Product


def get_user(db: Session, username: str) -> User:
    return db.query(User).filter(User.username == username).first()


def get_user_password(db: Session, username: str) -> str:
    user = db.query(User).filter(User.username == username).first()

    return user.password


def create_user(db: Session, user: models.UserCreate) -> User:
    db_user = User(username=user.username, password=user.password, role=user.role)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user


def deposit(db: Session, username: str, deposit: int) -> User:
    db_user_query = db.query(User).filter(User.username == username)
    db_user_query.update({"deposit": deposit})
    db.commit()

    db_user = db_user_query.first()
    db.refresh(db_user)

    return db_user


def get_products(db: Session) -> list[Product]:
    return db.query(Product).all()


def get_product(db: Session, product_name: str) -> Product:
    return db.query(Product).filter(Product.product_name == product_name).first()


def create_product(
    db: Session, new_product: models.Product, user: models.User
) -> Product:
    db_product = Product(
        product_name=new_product.product_name,
        amount_available=new_product.amount_available,
        cost=new_product.cost,
        seller_id=user.id,
    )
    db.add(db_product)
    db.commit()
    db.refresh(db_product)

    return db_product


def update_product(db: Session, product: models.ProductCreate) -> Product:
    db_product_query = db.query(Product).filter(
        Product.product_name == product.product_name
    )
    db_product_query.update(
        {
            "amount_available": product.amount_available,
            "product_name": product.product_name,
            "cost": product.cost,
        }
    )
    db.commit()

    db_product = db_product_query.first()
    db.refresh(db_product)

    return db_product


def delete_product(db: Session, product_id: int):
    db.query(Product).filter(Product.id == product_id).delete()
    db.commit()

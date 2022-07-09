from typing import List

from vending.db import execute, FetchType
from vending.models import DBProduct, DBUser, Product, RegisterUser


def get_user(username: str) -> DBUser:
    select_user_query = (
        "SELECT id, username, deposit, role FROM users WHERE username = :username"
    )
    user = execute(
        select_user_query, params={"username": username}, fetch=FetchType.FIRST
    )

    if not user:
        return None

    return DBUser(**user)


def get_user_password(username: str) -> str:
    select_pwd_query = "SELECT password FROM users WHERE username = :username"
    pwd = execute(
        select_pwd_query, params={"username": username}, fetch=FetchType.FIRST
    )["password"]

    return pwd


def create_user(user: RegisterUser):
    create_user_sql = "INSERT INTO users(username, password, role) VALUES (:username, :password, :role)"  # noqa
    params = {"username": user.username, "password": user.password, "role": user.role}
    execute(create_user_sql, params)


def deposit(user: DBUser):
    deposit_query = "UPDATE users SET deposit = :deposit WHERE id = :user_id"
    params = {"deposit": user.deposit, "user_id": user.id}
    execute(deposit_query, params)


def get_products() -> List[DBProduct]:
    select_products_query = "SELECT * FROM products"
    db_products = execute(select_products_query, fetch=FetchType.ALL)
    products = []

    for p in db_products:
        product = DBProduct(**p)
        products.append(product)

    return products


def get_product(product_name: str) -> DBProduct:
    select_product_data = "SELECT * FROM products WHERE product_name = :product_name"
    params = {"product_name": product_name}
    product = execute(select_product_data, params, fetch=FetchType.FIRST)

    if not product:
        return None

    return DBProduct(**product)


def create_product(new_product: Product, user: DBUser):
    create_product_query = "INSERT INTO products (amount_available, cost, product_name, seller_id) VALUES (:amount_available, :cost, :product_name, :user_id)"  # noqa
    params = new_product.dict()
    params["user_id"] = user.id
    execute(create_product_query, params=params)


def update_product(product: DBProduct):
    update_query = "UPDATE products SET amount_available = :amount_available, cost = :cost, product_name = :product_name WHERE id = :id"  # noqa
    execute(update_query, params=product.dict())


def delete_product(product_id: str):
    delete_product_query = "DELETE FROM products WHERE id = :product_id"
    execute(delete_product_query, params={"product_id": product_id})

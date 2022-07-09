import os
from sqlalchemy.sql import text

from vending.db import get_db, setup


TEST_DB = "test-db.sql"

# init DB for tests
def pytest_sessionstart(session):
    setup(TEST_DB)
    db = get_db()

    db.execute(
        text(
            "INSERT INTO users(username, password, role) VALUES (:username, :password, :role)"
        ),
        {"username": "test_buyer", "password": "not-secure", "role": "buyer"},
    )

    db.execute(
        text(
            "INSERT INTO users(username, password, role) VALUES (:username, :password, :role)"
        ),
        {"username": "test_seller", "password": "not-secure", "role": "seller"},
    )

    db.execute(
        text(
            "INSERT INTO products (amount_available, cost, product_name, seller_id) VALUES (:amount_available, :cost, :product_name, :user_id)"
        ),
        {
            "amount_available": 100,
            "cost": 5,
            "product_name": "test_product",
            "user_id": "1",
        },
    )

    db.commit()


# clean up
def pytest_sessionfinish(session, exitstatus):
    os.remove(TEST_DB)

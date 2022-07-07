from fastapi.testclient import TestClient
from unittest import mock
import pytest

from vending import app
from vending.auth import authorize_user
from vending.models import DBUser, DBProduct

client = TestClient(app)

mock_db_product = DBProduct(
    amount_available=100,
    cost=100,
    product_name="test_product",
    id="1",
    seller_id="1",
)

mock_db_user_buyer = DBUser(
    username="test", password="test_pwd", role="buyer", id=1, deposit=0
)

mock_db_user_buyer_with_money = DBUser(
    username="test", password="test_pwd", role="buyer", id=1, deposit=100
)

mock_db_user_seller = DBUser(
    username="test", password="test_pwd", role="seller", id=1, deposit=0
)


class TestDeposit:
    @mock.patch("vending.actions.deposit")
    def test_deposit_raises_422_for_no_data(self, mock_db_deposit, fastapi_dep):
        with fastapi_dep(app).override({authorize_user: mock_db_user_buyer}):
            response = client.post("/deposit")

            assert response.status_code == 422

    @mock.patch("vending.actions.deposit")
    def test_deposit_raises_400_for_seller(self, mock_db_deposit, fastapi_dep):
        with fastapi_dep(app).override({authorize_user: mock_db_user_seller}):
            response = client.post("/deposit", json={"amount": 1})

            assert response.status_code == 400
            assert response.json() == {
                "detail": "You must be a buyer in order to buy things and deposit coins"
            }

    @pytest.mark.parametrize(
        "amount, detail",
        [
            (-100, "deposit must be non-negative number"),
            (200, "Can't deposit more than 100"),
        ],
    )
    @mock.patch("vending.actions.deposit")
    def test_deposit_raises_400_for_bad_amount(
        self, mock_db_deposit, fastapi_dep, amount, detail
    ):
        with fastapi_dep(app).override({authorize_user: mock_db_user_buyer}):
            response = client.post("/deposit", json={"amount": amount})

            assert response.status_code == 400
            assert response.json() == {"detail": detail}

    @mock.patch("vending.actions.deposit")
    def test_deposit_200(self, mock_db_deposit, fastapi_dep):
        with fastapi_dep(app).override({authorize_user: mock_db_user_buyer}):
            response = client.post("/deposit", json={"amount": 5})

            assert response.status_code == 200
            mock_db_deposit.assert_called_with(
                DBUser(
                    username="test", password="test_pwd", role="buyer", id=1, deposit=5
                )
            )


class TestBuy:
    @mock.patch("vending.actions.deposit")
    @mock.patch("vending.actions.update_product")
    def test_buy_raises_422_for_no_data(
        self, mock_db_update_product, mock_db_deposit, fastapi_dep
    ):
        with fastapi_dep(app).override({authorize_user: mock_db_user_buyer}):
            response = client.post("/buy")

            assert response.status_code == 422

    @mock.patch("vending.actions.deposit")
    @mock.patch("vending.actions.update_product")
    def test_buy_raises_400_for_seller(
        self, mock_db_update_product, mock_db_deposit, fastapi_dep
    ):
        with fastapi_dep(app).override({authorize_user: mock_db_user_seller}):
            response = client.post(
                "/buy", json={"product_name": "test_product", "amount": 1}
            )

            assert response.status_code == 400
            assert response.json() == {
                "detail": "You must be a buyer in order to buy things and deposit coins"
            }

    @mock.patch("vending.actions.get_product")
    @mock.patch("vending.actions.deposit")
    @mock.patch("vending.actions.update_product")
    def test_buy_raises_400_for_not_enough_units(
        self, mock_db_update_product, mock_db_deposit, mock_get_product, fastapi_dep
    ):
        with fastapi_dep(app).override({authorize_user: mock_db_user_buyer}):
            mock_get_product.return_value = mock_db_product
            response = client.post(
                "/buy", json={"product_name": "test_product", "amount": 200}
            )

            assert response.status_code == 400
            assert response.json() == {
                "detail": "There is not enough units of this product."
            }

    @mock.patch("vending.actions.get_product")
    @mock.patch("vending.actions.deposit")
    @mock.patch("vending.actions.update_product")
    def test_buy_raises_400_for_not_enough_balance(
        self, mock_db_update_product, mock_db_deposit, mock_get_product, fastapi_dep
    ):
        with fastapi_dep(app).override({authorize_user: mock_db_user_buyer}):
            mock_get_product.return_value = mock_db_product
            response = client.post(
                "/buy", json={"product_name": "test_product", "amount": 1}
            )

            assert response.status_code == 400
            assert response.json() == {
                "detail": "You don't have enough coins to for this order."
            }

    @mock.patch("vending.actions.get_product")
    @mock.patch("vending.actions.deposit")
    @mock.patch("vending.actions.update_product")
    def test_buy_200(
        self, mock_db_update_product, mock_db_deposit, mock_get_product, fastapi_dep
    ):
        with fastapi_dep(app).override({authorize_user: mock_db_user_buyer_with_money}):
            mock_get_product.return_value = mock_db_product
            response = client.post(
                "/buy", json={"product_name": "test_product", "amount": 1}
            )

            assert response.status_code == 200
            assert response.json() == {
                "total_spent": 100,
                "products": ["test_product"],
                "amount": 1,
                "change": 0,
            }
            mock_db_update_product.assert_called_with(
                DBProduct(
                    **mock_db_product.dict(exclude={"amount_available"}),
                    amount_available=99
                )
            )
            mock_db_deposit.assert_called_with(
                DBUser(
                    **mock_db_user_buyer_with_money.dict(exclude={"deposit"}), deposit=0
                )
            )

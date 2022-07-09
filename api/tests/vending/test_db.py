from vending.db import actions
from vending.models import DBUser, RegisterUser


class TestDB:
    def test_get_user(self):
        db_user = actions.get_user("test_buyer")

        assert db_user.username == "test_buyer"

    def test_get_user_none(self):
        db_user = actions.get_user("no_user")

        assert db_user == None

    def test_create_user(self):
        actions.create_user(
            RegisterUser(username="another_user", password="not-secure", role="buyer")
        )

        db_user = actions.get_user("another_user")

        assert db_user.username == "another_user"

    def test_deposit(self):
        user = actions.get_user("test_buyer")
        user = DBUser(**user.dict(exclude={"deposit"}), deposit=100)

        actions.deposit(user)

        updated_user = actions.get_user("test_buyer")

        assert updated_user.deposit == 100

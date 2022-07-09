from vending.db import actions, get_db
from vending.models import UserCreate

db = get_db()


class TestDB:
    def test_get_user(self):
        db_user = actions.get_user(db, "test_buyer")

        assert db_user.username == "test_buyer"

    def test_get_user_none(self):
        db_user = actions.get_user(db, "no_user")

        assert db_user == None

    def test_create_user(self):
        user = actions.create_user(
            db, UserCreate(username="another_user", password="not-secure", role="buyer")
        )

        assert user.username == "another_user"

    def test_deposit(self):
        user = actions.get_user(db, "test_buyer")

        updated_user = actions.deposit(db, user.username, 100)

        assert updated_user.deposit == 100

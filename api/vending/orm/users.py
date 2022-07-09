from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from vending.db import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(20), unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    deposit = Column(Integer, default=0)
    role = Column(String(20), nullable=False)

    # products = relationship("Product", back_populates="seller_id")

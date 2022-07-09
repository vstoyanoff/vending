from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from vending.db import Base


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    product_name = Column(String(20), unique=True, index=True, nullable=False)
    amount_available = Column(Integer, nullable=False, default=0)
    cost = Column(Integer, nullable=False)
    seller_id = Column(Integer, ForeignKey("users.id"))

    # seller = relationship("User", back_populates="products")

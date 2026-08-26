from sqlalchemy import Column,Integer, String, Float,ForeignKey
from sqlalchemy.orm import sessionmaker,declarative_base
from sqlalchemy.sql.expression import text
from sqlalchemy.sql.sqltypes import TIMESTAMP
Base = declarative_base()
class Produk(Base):
    __tablename__ = "product"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    description = Column(String)
    price = Column(Float)
    quantity = Column(Integer)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, nullable=False)
    email = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    
    # Automatically stamps the time the user was created
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))


#cart goes here
class Cart(Base):
    __tablename__ = "cart_item"
    id = Column(Integer, primary_key=True, nullable=False)

    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    product_id = Column(Integer, nullable=False)
    quantity = Column(Integer, nullable=False, default=1)


class Blocklist(Base):
    __tablename__ = "blocklist_tokens"
    
    id = Column(Integer, primary_key=True, nullable=False)
    # The string must be unique so we don't accidentally blocklist the same token twice
    token = Column(String, unique=True, nullable=False)

    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))


class Order(Base):
    __tablename__ = "orders"
    
    # 1. The Receipt Header
    id = Column(Integer, primary_key=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    total_amount = Column(Float, nullable=False)
    
    # "Pending", "Shipped", or "Delivered"
    status = Column(String, nullable=False, default="Pending") 
    
    # Automatically stamps the exact millisecond the checkout button was pressed
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))


class OrderItem(Base):
    __tablename__ = "order_items"
    
    # 2. The Line Items on the Receipt
    id = Column(Integer, primary_key=True, nullable=False)
    
    # Links this specific item to the overarching order receipt above
    order_id = Column(Integer, ForeignKey("orders.id", ondelete="CASCADE"), nullable=False)
    
    # Links to the product, but if the admin deletes the product later, we don't want to delete the order history! (SET NULL)
    product_id = Column(Integer, ForeignKey("product.id", ondelete="SET NULL"), nullable=True)
    
    quantity = Column(Integer, nullable=False)
    
    # THE CRITICAL COLUMN: The historical price
    unit_price = Column(Float, nullable=False)

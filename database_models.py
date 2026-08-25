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
    __tablename__ = "blocklisted_tokens"
    
    id = Column(Integer, primary_key=True, nullable=False)
    # The string must be unique so we don't accidentally blocklist the same token twice
    token = Column(String, unique=True, nullable=False)

    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))

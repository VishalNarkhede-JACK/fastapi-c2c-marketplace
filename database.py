import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker,declarative_base
from dotenv import load_dotenv
load_dotenv()

SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")

if not SQLALCHEMY_DATABASE_URL:
    raise ValueError("No DATABASE_URL found in .env file!")
engine = create_engine(SQLALCHEMY_DATABASE_URL)
session = sessionmaker(autocommit = False, autoflush= False, bind=engine)
Base = declarative_base()



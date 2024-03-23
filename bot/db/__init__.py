"""Database module"""

import os

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

# database connection URI
DB_URI = os.getenv("DB_URI")

# engine maintaining connection
engine = create_engine(DB_URI, echo=True)


# base class for declarative class definitions
class Base(DeclarativeBase):
    pass


# get a sessionmaker
Session = sessionmaker(bind=engine, expire_on_commit=False)

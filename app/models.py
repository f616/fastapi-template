# app/models.py
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class User(Base):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)


class Inv(Base):
    __tablename__ = "inv"
    id = Column(Integer, primary_key=True, index=True)
    item_name = Column(String(255), nullable=False)
    quantity = Column(Integer, nullable=False)

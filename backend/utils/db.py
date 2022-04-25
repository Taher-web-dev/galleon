""" Database """

# import sys
from datetime import datetime

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import DateTime, Boolean, Column, Integer, String  # , ForeignKey
# from sqlalchemy.orm import relationship
from sqlalchemy.orm import sessionmaker
from .settings import settings

engine = create_engine(settings.database_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

db = SessionLocal()

class Otp(Base):
    """ Otp model """
    __tablename__ = "otp"
    msisdn       = Column(String, primary_key=True, index=True)
    code         = Column(String, nullable=False)
    confirmation = Column(String, nullable=True)
    tries        = Column(Integer, nullable=False, default=0)
    updated_at   = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    created_at   = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False, onupdate=datetime.utcnow)

class User(Base):
    """ User model """
    __tablename__ = "users"
    id         = Column(Integer, primary_key=True, index=True)
    name       = Column(String, unique=True, index=True, nullable=False)
    email      = Column(String, unique=True, index=True, nullable=True)
    msisdn     = Column(String, unique=True, index=True, nullable=False)
    password   = Column(String, nullable=False)
    session    = Column(String, nullable=True)
    is_active  = Column(Boolean(), default=True)
    profile_pic_url = Column(String, nullable=True)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False, onupdate=datetime.utcnow)

    @property
    def serialize(self) -> dict:
        """ Return in serializeable format """
        return {"name": self.name, "msisdn": self.msisdn, "profile_pic_url": self.profile_pic_url}

    # items = relationship("Item", back_populates="owner")


# class Item(Base):
#    __tablename__ = "items"
#    id = Column(Integer, primary_key=True, index=True)
#    title = Column(String, index=True)
#    description = Column(String, index=True)
#    owner_id = Column(Integer, ForeignKey("users.id"))
#    owner = relationship("User", back_populates="items")

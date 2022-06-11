"""DB Operations for the user package model"""

from db.main import SessionLocal
from db.models import User
from utils.password_hashing import hash_password
from .models.request import UserCreateRequest


def create_user(new_user: UserCreateRequest) -> User:
    with SessionLocal() as session:
        user = User(
            msisdn=new_user.msisdn,
            name=new_user.name,
            password=hash_password(new_user.password),
            email=new_user.email,
            profile_pic_url=new_user.profile_pic_url,
        )
        session.add(user)
        session.commit()
        session.refresh(user)
        return user


def get_user(msisdn: str) -> User | None:
    """Retrieve user by msisdn"""
    with SessionLocal() as session:
        return session.query(User).filter(User.msisdn == msisdn).first()


def update_user_password(user: User, password: str) -> None:
    with SessionLocal() as session:
        user.password = hash_password(password)
        session.add(user)
        session.commit()


def update_user(user: User, user_profile: UserCreateRequest) -> User:
    for key, value in user_profile.dict(exclude_none=True).items():
        setattr(user, key, value)
    with SessionLocal() as session:
        session.add(user)
        session.commit()
        session.refresh(user)
        return user


def delete_user(user: User) -> None:
    with SessionLocal() as session:
        session.delete(user)
        session.commit()


def update_user_refresh_token(user: User, refresh_token: str) -> None:
    with SessionLocal() as session:
        user.refresh_token = refresh_token
        session.add(user)
        session.commit()


def delete_user_refresh_token(user: User) -> None:
    with SessionLocal() as session:
        user.refresh_token = None
        session.add(user)
        session.commit()

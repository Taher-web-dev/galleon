""" User management apis """

from fastapi import APIRouter, Body, Header, HTTPException, status
from pydantic import BaseModel
from typing import Optional, Any
from fastapi import Request, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from utils.jwt import decode_jwt, sign_jwt
from utils.db import db, User
from utils.password_hashing import verify_password, get_password_hash


class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super(JWTBearer, self).__init__(auto_error=auto_error)

    async def __call__(self, request: Request) -> Optional[str]:
        try:
            credentials: Optional[HTTPAuthorizationCredentials] = await super(
                JWTBearer, self
            ).__call__(request)
            if credentials and credentials.scheme == "Bearer":
                return decode_jwt(credentials.credentials)["msisdn"]
        except:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated"
            )


router = APIRouter()


class UserCreate(BaseModel):
    otp_confirmation: str
    name: str
    msisdn: str
    password: str
    profile_pic_url: Optional[str]
    email: Optional[str]


class UserUpdate(BaseModel):
    name: Optional[str]
    email: Optional[str]
    password: Optional[str]
    profile_pic_url: Optional[str]


class UserRetrieve(BaseModel):
    id: int
    status: str
    name: Optional[str]
    email: Optional[str]
    profile_pic_url: Optional[str]


@router.post("/create", response_model=dict[str, Any])
async def create_user(new_user: UserCreate) -> dict[str, Any]:
    """Register a new user"""
    user = db.query(User).filter(User.msisdn == new_user.msisdn).first()
    if user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Customer already exists"
        )

    user = User(
        msisdn=new_user.msisdn,
        name=new_user.name,
        password=get_password_hash(new_user.password),
        email=new_user.email,
        profile_pic_url=new_user.profile_pic_url,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return {"user_id": user.id}


@router.get(
    "/profile",
    response_model=UserRetrieve,
    response_model_exclude_none=True,
)
async def get_profile(msisdn=Depends(JWTBearer())) -> UserRetrieve:
    """Get user profile"""
    user = db.query(User).filter(User.msisdn == msisdn).first()

    return UserRetrieve(
        status="success",
        id=user.id,
        name=user.name,
        email=user.email,
        profile_pic_url=user.profile_pic_url,
    )


@router.patch("/profile")
async def update_profile(user_profile: UserUpdate, msisdn=Depends(JWTBearer())):
    """Update user profile"""
    user = db.query(User).filter(User.msisdn == msisdn).first()

    if user_profile.name:
        user.name = user_profile.name
    if user_profile.password:
        user.password = user_profile.password
    if user_profile.email:
        user.email = user_profile.email
    if user_profile.profile_pic_url:
        user.profile_pic_url = user_profile.profile_pic_url
    db.commit()
    db.refresh(user)

    return {"status": "success"}


@router.post("/login")
async def login(msisdn: str = Body(...), password: str = Body(...)) -> dict:
    """Login and generate refresh token"""
    user = db.query(User).filter(User.msisdn == msisdn).first()
    if user and verify_password(password, user.password):
        access_token = sign_jwt({"msisdn": msisdn})
        refresh_token = sign_jwt({"msisdn": msisdn, "grant_type": "refresh"}, 86400)
        user.refresh_token = refresh_token["token"]
        db.commit()

        return {
            "status": "success",
            "refresh_token": refresh_token,
            "access_token": access_token,
        }

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, detail="Wrong credentials."
    )


@router.post("/logout")
async def logout(msisdn=Depends(JWTBearer())):
    """Logout (aka delete refresh token)"""
    user = db.query(User).filter(User.msisdn == msisdn).first()
    if user and user.refresh_token:
        user.refresh_token = None
        db.commit()
    return {"status": "success"}


@router.post("/token")
async def gen_access_token(refresh_token: Optional[str] = Header(None)):
    """Generate access token from provided refresh token"""

    if refresh_token is not None:
        data = decode_jwt(refresh_token)
        if "msisdn" in data:
            msisdn = data["msisdn"]
            user = db.query(User).filter(User.msisdn == "msisdn").first()
            if user is not None:
                return {
                    "status": "success",
                    "access_token": sign_jwt({"msisdn": msisdn}),
                }

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail={"message": "failed", "code": "99"},
    )


@router.post("/delete")
async def delete(msisdn=Depends(JWTBearer())):
    """Delete user"""
    user = db.query(User).filter(User.msisdn == msisdn).first()
    assert user
    db.delete(user)
    db.commit()
    return {"status": "success"}

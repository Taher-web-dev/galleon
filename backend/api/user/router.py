""" User management apis """

from typing import Union
from fastapi import APIRouter, Body, Header
from pydantic import BaseModel
from typing import Optional, Any
from fastapi import Request, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from utils.jwt import decode_jwt, sign_jwt, generate_refresh_token
from utils.db import db, User
from utils.error import Error


class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super(JWTBearer, self).__init__(auto_error=auto_error)

    async def __call__(self, request: Request) -> Optional[str]:
        credentials: Optional[HTTPAuthorizationCredentials] = await super(
            JWTBearer, self
        ).__call__(request)
        if credentials and credentials.scheme == "Bearer":
            return decode_jwt(credentials.credentials)


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


def generate_unauth_error():
    return {"status":"failed", "detail": "Not authenticated"}


@router.post('/create', response_model=dict[str,Any])
async def create_user(new_user: UserCreate) -> dict[str,Any]:
    """ Register a new user """
    user = db.query(User).filter(User.msisdn==new_user.msisdn).first()
    if user:
        return Error(message="Customer already exists").dict()

    user = User(
        msisdn=new_user.msisdn,
        name=new_user.name,
        password=new_user.password,
        email=new_user.email,
        profile_pic_url=new_user.profile_pic_url,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return {"user_id": user.id}

@router.get('/profile', response_model=Union[UserRetrieve, Any], response_model_exclude_none=True)
async def get_profile(payload = Depends(JWTBearer())) -> Union[UserRetrieve, Any]:
    """ Get user profile """
    if payload == None:
        return generate_unauth_error()
    
    msisdn = payload["msisdn"]
    
    user = db.query(User).filter(User.msisdn==msisdn).first()
    if not user.refresh_token:
         return generate_unauth_error()
     
    return UserRetrieve(
        status="success",
        id=user.id,
        name=user.name,
        email=user.email,
        profile_pic_url=user.profile_pic_url,
    )


@router.patch('/profile')
async def update_profile(user_profile: Union[UserUpdate, Any], payload = Depends(JWTBearer())):
    """ Update user profile """
    if payload == None:
        return generate_unauth_error()
    
    msisdn = payload["msisdn"]
    
    user = db.query(User).filter(User.msisdn==msisdn).first()
    if not user.refresh_token:
         return generate_unauth_error()
     
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
    
    return {"status":"success"}

@router.post("/login")
async def login(msisdn: str = Body(...), password: str = Body(...)) -> dict:
    """Login and generate refresh token"""
    user = db.query(User).filter(User.msisdn == msisdn).first()
    if user and password == user.password:
        token = sign_jwt({"msisdn": msisdn})
        access_token = token["access_token"]
        refresh_token = generate_refresh_token({"msisdn": msisdn})
        user.refresh_token = refresh_token
        db.commit()
        
        return {"status": "success", "refresh_token": refresh_token, "access_token": access_token}
    
    return Error().dict()

@router.post('/logout')
async def logout(payload = Depends(JWTBearer())):
    """ Logout (aka delete refresh token) """
    if payload == None:
        return generate_unauth_error()
    
    msisdn = payload["msisdn"]
    
    user = db.query(User).filter(User.msisdn==msisdn).first()
    if user and user.refresh_token:
        user.refresh_token = None
        db.commit()
        
    return {"status":"success"}

@router.post("/token")
async def gen_access_token(refresh_token: Optional[str] = Header(None)):
    """Generate access token from provided refresh token"""

@router.post('/token')
async def gen_access_token(refresh_token : Optional[str] = Header(default=None)):
    """ Generate access token from provided refresh token """
    if refresh_token is not None:
        data = decode_jwt(refresh_token)
        if "msisdn" in data:
            msisdn = data["msisdn"]
            user = db.query(User).filter(User.msisdn == "msisdn").first()
            if user is not None:
                return {"status": "success", "access_token" : sign_jwt({"msisdn": msisdn})}
            
    return {"status": "failed", "code": 99}


@router.post('/delete')
async def delete(payload = Depends(JWTBearer())):
    """ Delete user """
    if payload == None:
        return generate_unauth_error()
    
    msisdn = payload["msisdn"]
    user = db.query(User).filter(User.msisdn==msisdn).first()
    assert user
    db.delete(user)
    db.commit()
    
    return {"status": "success"}

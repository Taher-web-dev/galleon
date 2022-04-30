""" User management apis """

from fastapi import APIRouter, Body
from pydantic import BaseModel
from typing import Optional, Any
from fastapi import Request, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from utils.jwt import decode_jwt, sign_jwt
from utils.db import db, User
from utils.error import Error

class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super(JWTBearer, self).__init__(auto_error=auto_error)

    async def __call__(self, request: Request) -> str | None:
        credentials: HTTPAuthorizationCredentials | None = await super(JWTBearer, self).__call__(request)
        if credentials and credentials.scheme == "Bearer":
            return decode_jwt(credentials.credentials)["msisdn"]


router = APIRouter()

class NewUser(BaseModel):
    name: str
    msisdn: str
    email: Optional[str]
    password: str
    profile_pic_url : Optional[str]
    otp_confirmation : str

class UserProfile(BaseModel):
    id: int
    name: Optional[str]
    msisdn: Optional[str]
    email: Optional[str]
    password : Optional[str]
    profile_pic_url : Optional[str]

@router.post('/create', response_model=dict[str,Any])
async def create_user(new_user: NewUser) -> dict[str,Any]:
    """ Register a new user """
    user = db.query(User).filter(User.msisdn==new_user.msisdn).first()
    if user:
        return Error(message="Customer already exists").dict() 

    user = User(msisdn= new_user.msisdn, name=new_user.name, password= new_user.password, email= new_user.email, profile_pic_url = new_user.profile_pic_url)
    
    #if new_user.email:
    #    user.email = str(new_user.email)

    #if new_user.profile_pic_url:
    #    user.profile_pic_url = new_user.profile_pic_url

    db.add(user)
    db.commit()
    db.refresh(user)

    return {"user_id": user.id} 

@router.get('/profile', response_model=UserProfile, response_model_exclude_none=True)
async def get_profile(msisdn = Depends(JWTBearer())) -> UserProfile:
    """ Get user profile """
    user = db.query(User).filter(User.msisdn==msisdn).first()
    return UserProfile(
        id=user.id,
        name=user.name,
        msisdn=user.msisdn,
        email=user.email,
        password=None,
        profile_pic_url = user.profile_pic_url)

@router.patch('/profile')
async def update_profile(user_profile: UserProfile, msisdn = Depends(JWTBearer())):
    """ Update user profile """
    user = db.query(User).filter(User.msisdn==msisdn).first()
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
    return {}

@router.post('/login')
async def login(msisdn: str = Body(...), password: str = Body(...)) -> dict:
    """ Login and generate refresh token """
    user = db.query(User).filter(User.msisdn==msisdn).first()
    if user and  password == user.password:
        token = sign_jwt({"msisdn": msisdn})
        user.refresh_token = token["token"]
        db.commit()
        return {"refresh_token": token, "access_token": token}
    return Error().dict()

@router.post('/logout')
async def logtout(msisdn = Depends(JWTBearer())):
    """ Logout (aka delete refresh token) """
    user = db.query(User).filter(User.msisdn==msisdn).first()
    if user and user.refresh_token:
        user.refresh_token = ""
        db.commit()
    return {"status":"success"}


class Refresh(BaseModel):
    msisdn: str
    refresh_token: str

# FIXME get refresh token from header. access token shouldn't be required
@router.post('/token')
async def access(refresh: Refresh, msisdn=Depends(JWTBearer())):
    """ Generate access token """
    user = db.query(User).filter(User.msisdn==msisdn).first()
    assert refresh.msisdn == user.msisdn
    return {"access_token": refresh}

@router.post('/delete')
async def delete(msisdn = Depends(JWTBearer())):
    """ Delete user """
    user = db.query(User).filter(User.msisdn==msisdn).first()
    assert user
    db.delete(user)
    db.commit()
    return {"msisdn": msisdn}

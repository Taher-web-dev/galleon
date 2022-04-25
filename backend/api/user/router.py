
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
from fastapi import Request, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from utils.jwt import decode_jwt, sign_jwt
from utils.db import db, User

class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super(JWTBearer, self).__init__(auto_error=auto_error)

    async def __call__(self, request: Request) -> dict | None:
        credentials: HTTPAuthorizationCredentials | None = await super(JWTBearer, self).__call__(request)
        if credentials and credentials.scheme == "Bearer":
            return decode_jwt(credentials.credentials)


router = APIRouter()

class RegisterUser(BaseModel):
    name: str
    msisdn: str 
    password: str
    profile_pic_url : Optional[str]
    otp_confirmation : str

class UserProfile(BaseModel):
    name: str
    msisdn: str 
    password : Optional[str]
    profile_pic_url : Optional[str]

    #def __init__(self, name: str, msisdn: str, password: str | None = None, profile_pic_url: str | None = None):
    #    self.name = name
    #    self.msisdn = msisdn
    #    self.password = password
    #    self.profile_pic_url = profile_pic_url


@router.post('/register')
async def register(user: RegisterUser):
    """ Register a new user """
    return  user

@router.get('/profile', response_model=UserProfile, response_model_exclude_none=True)
async def get_profile(jwt: dict = Depends(JWTBearer())):
    """ Get user profile """
    user = db.query(User).filter(User.msisdn==jwt["msisdn"]).first()
    return UserProfile(
        name=user.name, 
        msisdn=user.msisdn,
        profile_pic_url = user.profile_pic_url) 

@router.post('/profile')
async def update_profile(user_profile: UserProfile, jwt: dict = Depends(JWTBearer())):
    """ Update user profile """
    user = db.query(User).filter(User.msisdn==jwt["msisdn"]).first()
    user.name = user.name
    if user_profile.password:
        user.password = user.password
    if user_profile.profile_pic_url:
        user.profile_pic_url = user.profile_pic_url
    return {"msisdn": user["msisdn"]} 

class Credentials(BaseModel):
    msisdn: str
    password: str

@router.post('/auth/refresh')
async def refresh(credentials: Credentials) -> dict:
    """ Generate refresh token """
    token = sign_jwt({"msisdn": credentials.msisdn}) 
    return {"msisdn": credentials.msisdn, "refresh_token": token, "access_token": token} 

class Refresh(BaseModel):
    msisdn: str
    refresh_token: str

@router.post('/auth/access')
async def access(refresh: Refresh, jwt : dict =Depends(JWTBearer())):
    """ Generate access token """
    user = db.query(User).filter(User.msisdn==jwt["msisdn"]).first()
    assert refresh.msisdn == user.msisdn
    return {"access_token": refresh} 

@router.post('/delete', dependencies=[Depends(JWTBearer())])
async def delete():
    """ Delete user """
    return {} 

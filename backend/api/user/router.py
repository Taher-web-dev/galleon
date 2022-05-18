""" User management apis """

from pydantic import BaseModel, Field
from fastapi import APIRouter, Body, Header, HTTPException, status, Request, Depends
from typing import Optional
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from utils.jwt import decode_jwt, sign_jwt
from utils.db import db, User
from utils.password_hashing import verify_password, hash_password
import utils.regex as rgx
from utils.api_responses import Status, ApiResponse


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


class UserProfile(BaseModel):
    id: int
    name: str
    msisdn: str = Field(..., regex=rgx.MSISDN)
    email: str | None = None
    password: str | None = None
    profile_pic_url: str | None = None


class UserProfileResponse(ApiResponse):
    data: UserProfile


class UserCreateRequest(BaseModel):
    name: str = Field(..., regex=rgx.TITLE)
    msisdn: str = Field(..., regex=rgx.DIGITS)
    password: str = Field(..., regex=rgx.PASSWORD)
    profile_pic_url: str = Field(None, regex=rgx.URL)
    email: str = Field(None, regex=rgx.EMAIL)


class UserUpdateRequest(BaseModel):
    name: str = Field(None, regex=rgx.TITLE)
    password: str = Field(None, regex=rgx.PASSWORD)
    profile_pic_url: str = Field(None, regex=rgx.URL)
    email: str = Field(None, regex=rgx.EMAIL)


@router.post("/create", response_model=ApiResponse, response_model_exclude_none=True)
async def create_user(new_user: UserCreateRequest) -> ApiResponse:
    """Register a new user"""
    user = db.query(User).filter(User.msisdn == new_user.msisdn).first()
    if user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Customer already exists"
        )

    user = User(
        msisdn=new_user.msisdn,
        name=new_user.name,
        password=hash_password(new_user.password),
        email=new_user.email,
        profile_pic_url=new_user.profile_pic_url,
    )

    db.add(user)
    db.commit()
    db.refresh(user)
    return ApiResponse(status=Status.success, data={"id": user.id})


@router.get(
    "/profile", response_model=UserProfileResponse, response_model_exclude_none=True
)
async def get_user_profile(msisdn=Depends(JWTBearer())) -> UserProfileResponse:
    """Get user profile"""
    user = db.query(User).filter(User.msisdn == msisdn).first()
    return UserProfileResponse(
        status=Status.success,
        data=UserProfile(
            id=user.id,
            msisdn=msisdn,
            name=user.name,
            email=user.email,
            profile_pic_url=user.profile_pic_url,
        ),
    )


@router.patch(
    "/profile", response_model=UserProfileResponse, response_model_exclude_none=True
)
async def update_profile(user_profile: UserUpdateRequest, msisdn=Depends(JWTBearer())):
    """Update user profile"""
    user = db.query(User).filter(User.msisdn == msisdn).first()

    if user_profile.name:
        user.name = user_profile.name
    if user_profile.password:
        user.password = hash_password(user_profile.password)
    if user_profile.email:
        user.email = user_profile.email
    if user_profile.profile_pic_url:
        user.profile_pic_url = user_profile.profile_pic_url
    db.commit()
    db.refresh(user)

    return UserProfileResponse(
        status=Status.success,
        data=UserProfile(
            id=user.id,
            msisdn=msisdn,
            name=user.name,
            email=user.email,
            profile_pic_url=user.profile_pic_url,
        ),
    )


@router.post("/login", response_model=ApiResponse, response_model_exclude_none=True)
async def login(
    msisdn: str = Body(..., regex=rgx.DIGITS),
    password: str = Body(..., regex=rgx.PASSWORD),
) -> ApiResponse:
    """Login and generate refresh token"""
    user = db.query(User).filter(User.msisdn == msisdn).first()
    if user and verify_password(password, user.password):
        access_token = sign_jwt({"msisdn": msisdn})
        refresh_token = sign_jwt({"msisdn": msisdn, "grant_type": "refresh"}, 86400)
        user.refresh_token = refresh_token
        db.commit()
        return ApiResponse(
            status=Status.success,
            data={"refresh_token": refresh_token, "access_token": access_token},
        )

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, detail="Wrong credentials."
    )


@router.post("/logout", response_model=ApiResponse, response_model_exclude_none=True)
async def logout(msisdn=Depends(JWTBearer())) -> ApiResponse:
    """Logout (aka delete refresh token)"""
    user = db.query(User).filter(User.msisdn == msisdn).first()
    if user and user.refresh_token:
        user.refresh_token = None
        db.commit()
    return ApiResponse(status=Status.success)


@router.post("/token", response_model=ApiResponse, response_model_exclude_none=True)
async def gen_access_token(refresh_token: Optional[str] = Header(None)) -> ApiResponse:
    """Generate access token from provided refresh token"""

    if refresh_token is not None:
        data = decode_jwt(refresh_token)
        if "msisdn" in data:
            msisdn = data["msisdn"]
            user = db.query(User).filter(User.msisdn == "msisdn").first()
            if user is not None:
                return ApiResponse(
                    status=Status.success,
                    data={
                        "refresh_token": refresh_token,
                        "access_token": sign_jwt({"msisdn": msisdn}),
                    },
                )

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail={"message": "failed", "code": "99"},
    )


@router.post("/delete", response_model=ApiResponse, response_model_exclude_none=True)
async def delete(msisdn=Depends(JWTBearer())) -> ApiResponse:
    """Delete user"""
    user = db.query(User).filter(User.msisdn == msisdn).first()
    assert user
    db.delete(user)
    db.commit()
    return ApiResponse(status=Status.success)

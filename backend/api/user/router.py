""" User management apis """

from fastapi import APIRouter, Body, Header, status, Depends
from typing import Optional
from api.models.response import SuccessResponse
from utils.jwt import decode_jwt, sign_jwt
from utils.db import db, User, Otp
from utils.password_hashing import verify_password, hash_password
import utils.regex as rgx
from utils.jwt import JWTBearer
from api.models.response import ApiException
from api.user.models.request import UserCreateRequest, UserUpdateRequest
from api.user.models.response import (
    Tokens,
    TokensResponse,
    UserProfile,
    UserProfileResponse,
)
from api.user.models import examples
import api.user.models.errors as err


router = APIRouter()


@router.post(
    "/create",
    response_model=UserProfileResponse,
    response_model_exclude_none=True,
    response_model_exclude_unset=True,
    responses=examples.create_user,
)
async def create_user(new_user: UserCreateRequest) -> UserProfileResponse:
    """Register a new user"""

    user = db.query(User).filter(User.msisdn == new_user.msisdn).first()
    if user:
        raise ApiException(status.HTTP_403_FORBIDDEN, err.USER_EXISTS)

    otp = db.query(Otp).filter(Otp.msisdn == new_user.msisdn).first()
    if not (otp and otp.confirmation and otp.confirmation == new_user.otp_confirmation):
        raise ApiException(status.HTTP_409_CONFLICT, err.INVALID_OTP)

    user = User(
        msisdn=new_user.msisdn,
        name=new_user.name,
        password=hash_password(new_user.password),
        email=new_user.email,
        profile_pic_url=new_user.profile_pic_url,
    )

    db.add(user)
    db.commit()
    user = db.query(User).filter(User.msisdn == new_user.msisdn).first()
    return UserProfileResponse(
        data=UserProfile(
            id=user.id,
            name=user.name,
            msisdn=user.msisdn,
            email=user.email,
            profile_pic_url=user.profile_pic_url,
        ),
    )


@router.get(
    "/profile",
    response_model=UserProfileResponse,
    response_model_exclude_none=True,
    responses=examples.get_user_profile,
)
async def get_user_profile(msisdn=Depends(JWTBearer())) -> UserProfileResponse:
    """Get user profile"""
    user = db.query(User).filter(User.msisdn == msisdn).first()
    return UserProfileResponse(
        data=UserProfile(
            id=user.id,
            msisdn=msisdn,
            name=user.name,
            email=user.email,
            profile_pic_url=user.profile_pic_url,
        ),
    )


@router.patch(
    "/profile",
    response_model=UserProfileResponse,
    response_model_exclude_none=True,
    responses=examples.update_profile,
)
async def update_profile(
    user_profile: UserUpdateRequest, msisdn=Depends(JWTBearer())
) -> UserProfileResponse:
    """Update user profile"""
    user = db.query(User).filter(User.msisdn == msisdn).first()

    for key, value in user_profile.dict(exclude_unset=True, exclude_none=True).items():
        if key == "password":
            user.password = hash_password(value)
        else:
            setattr(user, key, value)

    db.commit()
    db.refresh(user)

    return UserProfileResponse(
        data=UserProfile(
            id=user.id,
            msisdn=msisdn,
            name=user.name,
            email=user.email,
            profile_pic_url=user.profile_pic_url,
        ),
    )


@router.post(
    "/login",
    response_model=TokensResponse,
    response_model_exclude_none=True,
    responses=examples.login,
)
async def login(
    msisdn: str = Body(..., regex=rgx.MSISDN, max_length=20),
    password: str = Body(..., regex=rgx.PASSWORD, max_length=40),
) -> TokensResponse:
    """Login and generate refresh token"""
    user = db.query(User).filter(User.msisdn == msisdn).first()
    if user and verify_password(password, user.password):
        access_token = sign_jwt({"msisdn": msisdn})
        refresh_token = sign_jwt({"msisdn": msisdn, "grant_type": "refresh"}, 86400)
        user.refresh_token = refresh_token
        db.commit()
        return TokensResponse(
            data=Tokens(refresh_token=refresh_token, access_token=access_token),
        )

    raise ApiException(status.HTTP_401_UNAUTHORIZED, err.INVALID_CREDENTIALS)


@router.post(
    "/validate",
    response_model=SuccessResponse,
    response_model_exclude_none=True,
    responses=examples.login,
)
async def validate(
    msisdn=Depends(JWTBearer()),
    password: str = Body(..., regex=rgx.PASSWORD, max_length=40, embed=True),
) -> SuccessResponse:
    """Validate user password for logged-in users"""
    user = db.query(User).filter(User.msisdn == msisdn).first()
    if user and verify_password(password, user.password):
        return SuccessResponse()

    raise ApiException(status.HTTP_401_UNAUTHORIZED, err.INVALID_CREDENTIALS)


@router.post(
    "/logout",
    response_model=SuccessResponse,
    response_model_exclude_none=True,
    responses=examples.logout,
)
async def logout(msisdn=Depends(JWTBearer())) -> SuccessResponse:
    """Logout (aka delete refresh token)"""
    user = db.query(User).filter(User.msisdn == msisdn).first()
    if user and user.refresh_token:
        user.refresh_token = None
        db.commit()
    return SuccessResponse()


@router.post(
    "/token",
    response_model=TokensResponse,
    response_model_exclude_none=True,
    responses=examples.refresh_token,
)
async def gen_access_token(
    refresh_token: Optional[str] = Header(None),
) -> TokensResponse:
    """Generate access token from provided refresh token"""

    if refresh_token is not None:
        data = decode_jwt(refresh_token)
        if bool(data) and "msisdn" in data:
            msisdn = data["msisdn"]
            user = db.query(User).filter(User.msisdn == "msisdn").first()
            if user is not None:
                access_token = sign_jwt({"msisdn": msisdn})
                return TokensResponse(
                    data=Tokens(refresh_token=refresh_token, access_token=access_token),
                )

    raise ApiException(status.HTTP_401_UNAUTHORIZED, err.INVALID_REFRESH_TOKEN)


@router.post(
    "/delete",
    response_model=SuccessResponse,
    response_model_exclude_none=True,
    responses=examples.delete,
)
async def delete(msisdn=Depends(JWTBearer())) -> SuccessResponse:
    """Delete user"""
    user = db.query(User).filter(User.msisdn == msisdn).first()
    assert user
    db.delete(user)
    db.commit()
    return SuccessResponse()

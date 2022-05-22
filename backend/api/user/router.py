""" User management apis """

from fastapi import APIRouter, Body, Header, status, Depends
from typing import Optional
from api.base_response_models import StatusResponse
from utils.jwt import decode_jwt, sign_jwt
from utils.db import db, User, Otp
from utils.password_hashing import verify_password, hash_password
import utils.regex as rgx
from utils.jwt import JWTBearer
from utils.api_responses import Status, ApiException
from api.user.request_models import UserCreateRequest, UserUpdateRequest
from api.user.response_models import (
    Tokens,
    TokensResponse,
    UserProfile,
    UserProfileResponse,
)
import api.user.additional_responses as add_res
import api.user.app_errors as err


router = APIRouter()


@router.post(
    "/create",
    response_model=UserProfileResponse,
    response_model_exclude_none=True,
    response_model_exclude_unset=True,
    responses=add_res.create_user,
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
    responses=add_res.get_user_profile,
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
    responses=add_res.update_profile,
)
async def update_profile(
    user_profile: UserUpdateRequest, msisdn=Depends(JWTBearer())
) -> UserProfileResponse:
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
    responses=add_res.login,
)
async def login(
    msisdn: str = Body(..., regex=rgx.MSISDN),
    password: str = Body(..., regex=rgx.PASSWORD),
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
    "/logout",
    response_model=StatusResponse,
    response_model_exclude_none=True,
    responses=add_res.logout,
)
async def logout(msisdn=Depends(JWTBearer())) -> StatusResponse:
    """Logout (aka delete refresh token)"""
    user = db.query(User).filter(User.msisdn == msisdn).first()
    if user and user.refresh_token:
        user.refresh_token = None
        db.commit()
    return StatusResponse(status=Status.success)


@router.post(
    "/token",
    response_model=TokensResponse,
    response_model_exclude_none=True,
    responses=add_res.token,
)
async def gen_access_token(
    refresh_token: Optional[str] = Header(None),
) -> TokensResponse:
    """Generate access token from provided refresh token"""

    if refresh_token is not None:
        data = decode_jwt(refresh_token)
        if "msisdn" in data:
            msisdn = data["msisdn"]
            user = db.query(User).filter(User.msisdn == "msisdn").first()
            if user is not None:
                access_token = sign_jwt({"msisdn": msisdn})
                return TokensResponse(
                    data=Tokens(refresh_token=refresh_token, access_token=access_token),
                )

    raise ApiException(status.HTTP_401_UNAUTHORIZED, err.INVALID_TOKEN)


@router.post(
    "/delete",
    response_model=StatusResponse,
    response_model_exclude_none=True,
    responses=add_res.delete,
)
async def delete(msisdn=Depends(JWTBearer())) -> StatusResponse:
    """Delete user"""
    user = db.query(User).filter(User.msisdn == msisdn).first()
    assert user
    db.delete(user)
    db.commit()
    return StatusResponse(status=Status.success)

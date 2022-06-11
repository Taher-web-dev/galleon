""" User management apis """

from fastapi import APIRouter, Body, Header, status, Depends
from sqlalchemy.orm import Session
from typing import Optional
from api.models.response import ApiResponse
from utils.jwt import decode_jwt, sign_jwt
from db.models import User, Otp
from utils.password_hashing import verify_password
import utils.regex as rgx
from utils.jwt import JWTBearer
from api.models.response import ApiException
from api.models.errors import ELIGIBILITY_ERR
from utils.settings import settings
from api.user.models.request import (
    UserCreateRequest,
    UserResetPasswordRequest,
    UserUpdateRequest,
)
from api.user.models.response import (
    Tokens,
    TokensResponse,
    UserProfile,
    GetUserProfile,
    UserProfileResponse,
    GetUserProfileResponse,
)
from api.user.models import examples
import api.user.models.errors as err
from api.number.zend import zend_sim, is_4g_compatible
from .repository import (
    get_user,
    create_user,
    update_user_password,
    update_user,
    delete_user,
    update_user_refresh_token,
    delete_user_refresh_token,
)
from api.otp.repository import get_otp

router = APIRouter()


@router.post(
    "/create",
    response_model=UserProfileResponse,
    response_model_exclude_none=True,
    responses=examples.create_user,
)
async def register_user(new_user: UserCreateRequest) -> UserProfileResponse:
    """Register a new user"""
    if not zend_sim(new_user.msisdn)["is_eligible"]:
        raise ApiException(status.HTTP_403_FORBIDDEN, error=ELIGIBILITY_ERR)
    user = get_user(new_user.msisdn)
    if user:
        raise ApiException(status.HTTP_403_FORBIDDEN, err.USER_EXISTS)

    otp = get_otp(new_user.msisdn)
    if not (otp and otp.confirmation and otp.confirmation == new_user.otp_confirmation):
        raise ApiException(status.HTTP_409_CONFLICT, err.INVALID_OTP)

    user = create_user(new_user)
    return UserProfileResponse(
        data=UserProfile(
            id=user.id,
            name=user.name,
            msisdn=user.msisdn,
            email=user.email,
            profile_pic_url=user.profile_pic_url,
        ),
    )


@router.post(
    "/reset_password", response_model=ApiResponse, response_model_exclude_none=True
)
async def reset_password(reset: UserResetPasswordRequest) -> ApiResponse:
    """Reset a new password"""

    user: User = get_user(reset.msisdn)
    if not user:
        raise ApiException(status.HTTP_403_FORBIDDEN, err.INVALID_CREDENTIALS)

    otp: Otp = get_otp(reset.msisdn)
    # print(otp.confirmation, reset.otp_confirmation)
    if not (otp and otp.confirmation and otp.confirmation == reset.otp_confirmation):
        raise ApiException(status.HTTP_409_CONFLICT, err.INVALID_OTP)

    update_user_password(user, reset.password)
    return ApiResponse()


@router.get(
    "/profile",
    response_model=GetUserProfileResponse,
    response_model_exclude_none=True,
    responses=examples.get_user_profile,
)
async def get_user_profile(
    user=Depends(JWTBearer(fetch_user=True)),
) -> UserProfileResponse:
    """Get user profile"""
    return GetUserProfileResponse(
        data=GetUserProfile(
            id=user.id,
            msisdn=user.msisdn,
            name=user.name,
            email=user.email,
            is_4g_compatible=is_4g_compatible(user.msisdn),
            primary_offering_id=zend_sim(user.msisdn)["primary_offering_id"],
            unified_sim_status=zend_sim(user.msisdn)["unified_sim_status"],
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
    user_profile: UserUpdateRequest, user=Depends(JWTBearer(fetch_user=True))
) -> UserProfileResponse:
    """Update user profile"""
    updated_user = update_user(user, user_profile)

    return UserProfileResponse(
        data=UserProfile(
            id=updated_user.id,
            msisdn=updated_user.msisdn,
            name=updated_user.name,
            email=updated_user.email,
            profile_pic_url=updated_user.profile_pic_url,
        ),
    )


@router.post(
    "/login",
    response_model=TokensResponse,
    response_model_exclude_none=True,
    responses=examples.login,
)
async def login(
    msisdn: str = Body(..., regex=rgx.MSISDN, example="7839921514"),
    password: str = Body(..., regex=rgx.PASSWORD, max_length=40),
) -> TokensResponse:
    """Login and generate a refresh token"""
    user = get_user(msisdn)
    if user and verify_password(password, user.password):
        access_token = sign_jwt({"msisdn": msisdn})
        refresh_token = sign_jwt(
            {"msisdn": msisdn, "grant_type": "refresh"}, settings.jwt_refresh_expires
        )
        update_user_refresh_token(user, refresh_token)
        return TokensResponse(
            data=Tokens(
                refresh_token=refresh_token,
                access_token=access_token,
            ),
        )

    raise ApiException(status.HTTP_401_UNAUTHORIZED, err.INVALID_CREDENTIALS)


@router.post(
    "/validate",
    response_model=ApiResponse,
    response_model_exclude_none=True,
    responses=examples.login,
)
async def validate_user_password(
    user: User = Depends(JWTBearer(fetch_user=True)),
    password: str = Body(..., regex=rgx.PASSWORD, max_length=40, embed=True),
) -> ApiResponse:
    """Validate user password for logged-in users"""
    if user and verify_password(password, user.password):
        return ApiResponse()
    else:
        raise ApiException(status.HTTP_401_UNAUTHORIZED, err.INVALID_CREDENTIALS)


@router.delete(
    "/logout",
    response_model=ApiResponse,
    response_model_exclude_none=True,
    responses=examples.logout,
)
async def logout(user=Depends(JWTBearer(fetch_user=True))) -> ApiResponse:
    """Logout (aka delete refresh token)"""
    delete_user_refresh_token(user)
    return ApiResponse()


@router.post(
    "/token",
    response_model=TokensResponse,
    response_model_exclude_none=True,
    responses=examples.refresh_token,
)
async def generate_access_token(
    refresh_token: Optional[str] = Header(None),
) -> TokensResponse:
    """Generate access token from provided refresh token"""
    try:
        data = decode_jwt(refresh_token)
        if not data.get("grant_type", None):
            raise ApiException(
                status.HTTP_401_UNAUTHORIZED, error=err.INVALID_REFRESH_TOKEN
            )
        if bool(data) and "msisdn" in data:
            msisdn = data["msisdn"]
            user = get_user(msisdn)
            if user is not None:
                access_token = sign_jwt({"msisdn": msisdn})
                return TokensResponse(
                    data=Tokens(refresh_token=refresh_token, access_token=access_token),
                )
        if "msisdn" not in data:
            raise ApiException(
                status.HTTP_401_UNAUTHORIZED, error=err.INVALID_REFRESH_TOKEN
            )
    except:
        raise ApiException(
            status.HTTP_401_UNAUTHORIZED, error=err.INVALID_REFRESH_TOKEN
        )


@router.delete(
    "/delete",
    response_model=ApiResponse,
    response_model_exclude_none=True,
    responses=examples.delete,
)
async def delete(user=Depends(JWTBearer(fetch_user=True))) -> ApiResponse:
    """Delete user account"""
    delete_user(user)
    return ApiResponse()

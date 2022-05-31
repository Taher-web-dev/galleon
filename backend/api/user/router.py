""" User management apis """

from fastapi import APIRouter, Body, Header, status, Depends, Request
from typing import Optional
from api.models.response import ApiResponse
from utils.jwt import decode_jwt, sign_jwt
from db.models import User, Otp
from utils.password_hashing import verify_password, hash_password
import utils.regex as rgx
from utils.jwt import JWTBearer
from api.models.response import ApiException
from api.user.models.request import (
    UserCreateRequest,
    UserResetPasswordRequest,
    UserUpdateRequest,
)
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
    responses=examples.create_user,
)
async def create_user(
    new_user: UserCreateRequest, request: Request
) -> UserProfileResponse:
    """Register a new user"""

    user = request.state.db.query(User).filter(User.msisdn == new_user.msisdn).first()
    if user:
        raise ApiException(status.HTTP_403_FORBIDDEN, err.USER_EXISTS)

    otp = request.state.db.query(Otp).filter(Otp.msisdn == new_user.msisdn).first()
    if not (otp and otp.confirmation and otp.confirmation == new_user.otp_confirmation):
        raise ApiException(status.HTTP_409_CONFLICT, err.INVALID_OTP)

    user = User(
        msisdn=new_user.msisdn,
        name=new_user.name,
        password=hash_password(new_user.password),
        email=new_user.email,
        profile_pic_url=new_user.profile_pic_url,
    )

    request.state.db.add(user)
    request.state.db.commit()
    user = request.state.db.query(User).filter(User.msisdn == new_user.msisdn).first()
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
async def reset_password(
    reset: UserResetPasswordRequest, request: Request
) -> ApiResponse:
    """Register a new user"""

    user = request.state.db.query(User).filter(User.msisdn == reset.msisdn).first()
    if not user:
        raise ApiException(status.HTTP_403_FORBIDDEN, err.INVALID_CREDENTIALS)

    otp = request.state.db.query(Otp).filter(Otp.msisdn == reset.msisdn).first()
    if not (otp and otp.confirmation and otp.confirmation == reset.otp_confirmation):
        raise ApiException(status.HTTP_409_CONFLICT, err.INVALID_OTP)

    user.password = hash_password(reset.password)
    request.state.db.commit()
    return ApiResponse()


@router.get(
    "/profile",
    response_model=UserProfileResponse,
    response_model_exclude_none=True,
    responses=examples.get_user_profile,
)
async def get_user_profile(
    user=Depends(JWTBearer(fetch_user=True)),
) -> UserProfileResponse:
    """Get user profile"""

    return UserProfileResponse(
        data=UserProfile(
            id=user.id,
            msisdn=user.msisdn,
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
    request: Request,
    user_profile: UserUpdateRequest,
    user=Depends(JWTBearer(fetch_user=True)),
) -> UserProfileResponse:
    """Update user profile"""
    for key, value in user_profile.dict(exclude_none=True).items():
        setattr(user, key, value)

    request.state.db.commit()
    request.state.db.refresh(user)

    return UserProfileResponse(
        data=UserProfile(
            id=user.id,
            msisdn=user.msisdn,
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
    request: Request,
    msisdn: str = Body(..., regex=rgx.MSISDN, max_length=20),
    password: str = Body(..., regex=rgx.PASSWORD, max_length=40),
) -> TokensResponse:
    """Login and generate refresh token"""
    user = request.state.db.query(User).filter(User.msisdn == msisdn).first()
    if user and verify_password(password, user.password):
        access_token = sign_jwt({"msisdn": msisdn})
        refresh_token = sign_jwt({"msisdn": msisdn, "grant_type": "refresh"}, 86400)
        user.refresh_token = refresh_token
        request.state.db.commit()
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
async def validate(
    request: Request,
    msisdn=Depends(JWTBearer()),
    password: str = Body(..., regex=rgx.PASSWORD, max_length=40, embed=True),
) -> ApiResponse:
    """Validate user password for logged-in users"""
    user = request.state.db.query(User).filter(User.msisdn == msisdn).first()
    if user and verify_password(password, user.password):
        return ApiResponse()

    raise ApiException(status.HTTP_401_UNAUTHORIZED, err.INVALID_CREDENTIALS)


@router.post(
    "/logout",
    response_model=ApiResponse,
    response_model_exclude_none=True,
    responses=examples.logout,
)
async def logout(
    request: Request, user=Depends(JWTBearer(fetch_user=True))
) -> ApiResponse:
    """Logout (aka delete refresh token)"""
    user.refresh_token = None
    request.state.db.commit()
    return ApiResponse()


@router.post(
    "/token",
    response_model=TokensResponse,
    response_model_exclude_none=True,
    responses=examples.refresh_token,
)
async def gen_access_token(
    request: Request,
    refresh_token: Optional[str] = Header(None),
) -> TokensResponse:
    """Generate access token from provided refresh token"""
    if refresh_token is not None:
        data = decode_jwt(refresh_token)
        if bool(data) and "msisdn" in data:
            msisdn = data["msisdn"]
            user = request.state.db.query(User).filter(User.msisdn == msisdn).first()
            if user is not None:
                access_token = sign_jwt({"msisdn": msisdn})
                return TokensResponse(
                    data=Tokens(refresh_token=refresh_token, access_token=access_token),
                )

    raise ApiException(status.HTTP_401_UNAUTHORIZED, err.INVALID_REFRESH_TOKEN)


@router.delete(
    "/delete",
    response_model=ApiResponse,
    response_model_exclude_none=True,
    responses=examples.delete,
)
async def delete(
    request: Request, user=Depends(JWTBearer(fetch_user=True))
) -> ApiResponse:
    """Delete user"""
    request.state.db.delete(user)
    request.state.db.commit()
    return ApiResponse()

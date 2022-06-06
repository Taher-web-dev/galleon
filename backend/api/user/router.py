""" User management apis """

from fastapi import APIRouter, Body, Header, status, Depends
from db.main import get_db
from sqlalchemy.orm import Session
from typing import Optional
from api.models.response import ApiResponse
from utils.jwt import decode_jwt, sign_jwt
from db.models import User, Otp
from utils.password_hashing import verify_password, hash_password
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
from .check_eligibility import check_eligibility
from api.number.zend import zend_sim
from api.number.sim import get_unified_sim_status
from .check_support_4G import check_support_4G

router = APIRouter()


@router.post(
    "/create",
    response_model=UserProfileResponse,
    response_model_exclude_none=True,
    responses=examples.create_user,
)
async def create_user(
    new_user: UserCreateRequest, db: Session = Depends(get_db)
) -> UserProfileResponse:
    """Register a new user"""
    if not check_eligibility(new_user.msisdn):
        raise ApiException(status.HTTP_403_FORBIDDEN, error=ELIGIBILITY_ERR)
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


@router.post(
    "/reset_password", response_model=ApiResponse, response_model_exclude_none=True
)
async def reset_password(
    reset: UserResetPasswordRequest, db: Session = Depends(get_db)
) -> ApiResponse:
    """Register a new user"""

    user = db.query(User).filter(User.msisdn == reset.msisdn).first()
    if not user:
        raise ApiException(status.HTTP_403_FORBIDDEN, err.INVALID_CREDENTIALS)

    otp = db.query(Otp).filter(Otp.msisdn == reset.msisdn).first()
    if not (otp and otp.confirmation and otp.confirmation == reset.otp_confirmation):
        raise ApiException(status.HTTP_409_CONFLICT, err.INVALID_OTP)

    user.password = hash_password(reset.password)
    db.commit()
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
    backend_sim_status = zend_sim(user.msisdn)
    unified_sim_status = get_unified_sim_status(backend_sim_status)
    return GetUserProfileResponse(
        data=GetUserProfile(
            id=user.id,
            msisdn=user.msisdn,
            name=user.name,
            email=user.email,
            is_4g_compatible=check_support_4G(user.msisdn),
            unified_sim_status=unified_sim_status,
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
    user_profile: UserUpdateRequest,
    user=Depends(JWTBearer(fetch_user=True)),
    db: Session = Depends(get_db),
) -> UserProfileResponse:
    """Update user profile"""
    for key, value in user_profile.dict(exclude_none=True).items():
        setattr(user, key, value)

    db.commit()
    db.refresh(user)

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
    msisdn: str = Body(..., regex=rgx.MSISDN, example="7839921514"),
    password: str = Body(..., regex=rgx.PASSWORD, max_length=40),
    db: Session = Depends(get_db),
) -> TokensResponse:
    """Login and generate refresh token"""
    user = db.query(User).filter(User.msisdn == msisdn).first()
    if user and verify_password(password, user.password):
        access_token = sign_jwt({"msisdn": msisdn})
        refresh_token = sign_jwt(
            {"msisdn": msisdn, "grant_type": "refresh"}, settings.jwt_refresh_expires
        )
        user.refresh_token = refresh_token
        db.commit()
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
    db: Session = Depends(get_db),
    msisdn=Depends(JWTBearer()),
    password: str = Body(..., regex=rgx.PASSWORD, max_length=40, embed=True),
) -> ApiResponse:
    """Validate user password for logged-in users"""
    user = db.query(User).filter(User.msisdn == msisdn).first()
    if user and verify_password(password, user.password):
        return ApiResponse()

    # raise ApiException(status.HTTP_401_UNAUTHORIZED, err.INVALID_CREDENTIALS)


@router.delete(
    "/logout",
    response_model=ApiResponse,
    response_model_exclude_none=True,
    responses=examples.logout,
)
async def logout(
    user=Depends(JWTBearer(fetch_user=True)), db: Session = Depends(get_db)
) -> ApiResponse:
    """Logout (aka delete refresh token)"""
    user.refresh_token = None
    db.commit()
    return ApiResponse()


@router.post(
    "/token",
    response_model=TokensResponse,
    response_model_exclude_none=True,
    responses=examples.refresh_token,
)
async def gen_access_token(
    refresh_token: Optional[str] = Header(None), db: Session = Depends(get_db)
) -> TokensResponse:
    """Generate access token from provided refresh token"""
    try:
        data = decode_jwt(refresh_token)
        if bool(data) and "msisdn" in data:
            msisdn = data["msisdn"]
            user = db.query(User).filter(User.msisdn == msisdn).first()
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
async def delete(
    user=Depends(JWTBearer(fetch_user=True)), db: Session = Depends(get_db)
) -> ApiResponse:
    """Delete user"""
    db.delete(user)
    db.commit()
    return ApiResponse()

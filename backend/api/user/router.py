""" User management apis """

from pydantic import BaseModel, Field
from fastapi import APIRouter, Body, Header, status, Request, Depends
from typing import Optional
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from utils.jwt import decode_jwt, sign_jwt
from utils.db import db, User, Otp
from utils.password_hashing import verify_password, hash_password
import utils.regex as rgx
from utils.api_responses import Status, ApiResponse, Error, ApiException


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
            raise ApiException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                error=Error(type="jwtauth", code=10, message="Not authenticated"),
            )


router = APIRouter()


class UserProfile(BaseModel):
    id: int
    name: str
    msisdn: str = Field(..., regex=rgx.MSISDN)
    email: str | None = None
    password: str | None = None
    profile_pic_url: str | None = None


class UserCreateRequest(BaseModel):
    msisdn: str = Field(..., regex=rgx.DIGITS)
    name: str = Field(..., regex=rgx.TITLE)
    password: str = Field(..., regex=rgx.PASSWORD)
    email: str = Field(None, regex=rgx.EMAIL)
    profile_pic_url: str = Field(None, regex=rgx.URL)
    otp_confirmation: str = Field(..., regex=rgx.STRING)


class UserUpdateRequest(BaseModel):
    name: str = Field(None, regex=rgx.TITLE)
    password: str = Field(None, regex=rgx.PASSWORD)
    profile_pic_url: str = Field(None, regex=rgx.URL)
    email: str = Field(None, regex=rgx.EMAIL)


USER_EXISTS_ERROR = Error(
    type="user", code=201, message="Sorry the msisdn is already registered."
)
INVALID_OTP_ERROR = Error(
    type="otp",
    code=202,
    message="The confirmation provided is not valid please try again.",
)
INVALID_CREDENTIALS_ERROR = Error(
    type="auth",
    code=203,
    message="Invalid credentials",
)

INVALID_TOKEN_ERROR = Error(
    type="auth",
    code=204,
    message="Invalid token",
)


class UserExistsErrorResponse(ApiResponse):
    status: Status = Status.failed
    errors: list[Error] = [USER_EXISTS_ERROR]


class InvalidOtpErrorResponse(ApiResponse):
    status: Status = Status.failed
    errors: list[Error] = [INVALID_OTP_ERROR]


class InvalidTokenErrorResponse(ApiResponse):
    status: Status = Status.failed
    errors: list[Error] = [INVALID_TOKEN_ERROR]


class InvalidCredentialsErrorResponse(ApiResponse):
    status: Status = Status.failed
    errors: list[Error] = [INVALID_CREDENTIALS_ERROR]


class CreateUser(BaseModel):
    """Create User Response Model"""

    id: int
    msisdn: str
    name: str
    email: Optional[str]
    profile_pic_url: Optional[str]


@router.post(
    "/create",
    response_model=ApiResponse,
    response_model_exclude_none=True,
    responses={
        status.HTTP_403_FORBIDDEN: {
            "model": UserExistsErrorResponse,
            "description": "User already exists.",
        },
        status.HTTP_409_CONFLICT: {
            "model": InvalidOtpErrorResponse,
            "description": "Invalid OTP Confirmation.",
        },
    },
)
async def create_user(new_user: UserCreateRequest) -> ApiResponse:
    """Register a new user"""

    user = db.query(User).filter(User.msisdn == new_user.msisdn).first()
    if user:
        raise ApiException(
            status_code=status.HTTP_403_FORBIDDEN, error=USER_EXISTS_ERROR
        )

    otp = db.query(Otp).filter(Otp.msisdn == new_user.msisdn).first()
    if not (otp and otp.confirmation and otp.confirmation == new_user.otp_confirmation):
        raise ApiException(
            status_code=status.HTTP_409_CONFLICT, error=INVALID_OTP_ERROR
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
    user = db.query(User).filter(User.msisdn == new_user.msisdn).first()
    return ApiResponse(
        status=Status.success,
        data=UserProfile(
            id=user.id,
            name=user.name,
            msisdn=user.msisdn,
            email=user.email,
            profile_pic_url=user.profile_pic_url,
        ),
    )


@router.get("/profile", response_model=ApiResponse, response_model_exclude_none=True)
async def get_user_profile(msisdn=Depends(JWTBearer())) -> ApiResponse:
    """Get user profile"""
    user = db.query(User).filter(User.msisdn == msisdn).first()
    return ApiResponse(
        status=Status.success,
        data=UserProfile(
            id=user.id,
            msisdn=msisdn,
            name=user.name,
            email=user.email,
            profile_pic_url=user.profile_pic_url,
        ),
    )


@router.patch("/profile", response_model=ApiResponse, response_model_exclude_none=True)
async def update_profile(
    user_profile: UserUpdateRequest, msisdn=Depends(JWTBearer())
) -> ApiResponse:
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

    return ApiResponse(
        status=Status.success,
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
    response_model=ApiResponse,
    response_model_exclude_none=True,
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "model": InvalidCredentialsErrorResponse,
            "description": "Invalid credentials",
        },
    },
)
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

    raise ApiException(
        status_code=status.HTTP_401_UNAUTHORIZED, error=INVALID_CREDENTIALS_ERROR
    )


@router.post(
    "/logout",
    response_model=ApiResponse,
    response_model_exclude_none=True,
)
async def logout(msisdn=Depends(JWTBearer())) -> ApiResponse:
    """Logout (aka delete refresh token)"""
    user = db.query(User).filter(User.msisdn == msisdn).first()
    if user and user.refresh_token:
        user.refresh_token = None
        db.commit()
    return ApiResponse(status=Status.success)


@router.post(
    "/token",
    response_model=ApiResponse,
    response_model_exclude_none=True,
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "model": InvalidTokenErrorResponse,
            "description": "Invalid token.",
        },
    },
)
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

    raise ApiException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        error=INVALID_TOKEN_ERROR,
    )


@router.post("/delete", response_model=ApiResponse, response_model_exclude_none=True)
async def delete(msisdn=Depends(JWTBearer())) -> ApiResponse:
    """Delete user"""
    user = db.query(User).filter(User.msisdn == msisdn).first()
    assert user
    db.delete(user)
    db.commit()
    return ApiResponse(status=Status.success)

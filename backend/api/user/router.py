""" User management apis """

from pydantic import BaseModel, Field
from fastapi import APIRouter, Body, Header, HTTPException, status, Request, Depends
from typing import Optional
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import JSONResponse
from utils.jwt import decode_jwt, sign_jwt
from utils.db import db, User, Otp
from utils.password_hashing import verify_password, hash_password
import utils.regex as rgx
from utils.api_responses import Status, ApiResponse, Error


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


class UserRetrieve(BaseModel):
    id: int
    status: str
    name: Optional[str]
    email: Optional[str]
    profile_pic_url: Optional[str]


class LoginOut(Error):
    status: str
    refresh_token: dict
    access_token: dict


class UserExistsErr(Error):
    type: str = "error"  # TODO define a better error type here
    code: int = 201
    message: str = "Sorry the msisdn is already registered."


class InvalidOTPErr(Error):
    type: str = "error"  # TODO define a better error type here
    code: int = 202
    message: str = "The confirmation provided is not valid please try again."


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
            "model": ApiResponse(status=Status.failed, errors=[UserExistsErr().dict()]),
            "description": "User already exists.",
        },
        status.HTTP_409_CONFLICT: {
            "model": ApiResponse(status=Status.failed, errors=[InvalidOTPErr().dict()]),
            "description": "Invalid OTP Confirmation.",
        },
    },
)
async def create_user(new_user: UserCreateRequest) -> ApiResponse:
    """Register a new user"""
    user = db.query(User).filter(User.msisdn == new_user.msisdn).first()
    if user:
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content=ApiResponse(
                status=Status.failed, errors=[UserExistsErr().dict()]
            ).dict(),
        )

    otp = db.query(Otp).filter(Otp.msisdn == new_user.msisdn).first()
    if not (otp and otp.confirmation and otp.confirmation == new_user.otp_confirmation):
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content=ApiResponse(
                status=Status.failed, errors=[InvalidOTPErr().dict()]
            ).dict(),
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
    return ApiResponse(status=Status.success, data=CreateUser(**user.serialize).dict())


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

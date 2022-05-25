import jwt
from time import time
from typing import Optional
from fastapi import Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from utils.settings import settings
from api.models.response import ApiException
import api.models.errors as api_errors


class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super().__init__(auto_error=auto_error)

    async def __call__(self, request: Request) -> Optional[str]:
        try:
            credentials: Optional[
                HTTPAuthorizationCredentials
            ] = await super().__call__(request)
            if credentials and credentials.scheme == "Bearer":
                decoded_data = decode_jwt(credentials.credentials)
                if not decoded_data:
                    raise ApiException(
                        status.HTTP_401_UNAUTHORIZED, api_errors.EXPIRED_TOKEN
                    )
                # TODO attach logged-in user to the request object
                return decoded_data.get("msisdn")

        except:
            raise ApiException(
                status.HTTP_401_UNAUTHORIZED, api_errors.NOT_AUTHENTICATED
            )


def sign_jwt(data: dict, expires: int = 600) -> str:
    payload = {"data": data, "expires": time() + expires}
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def decode_jwt(token: str) -> dict:
    decoded_token = jwt.decode(
        token, settings.jwt_secret, algorithms=[settings.jwt_algorithm]
    )
    return decoded_token["data"] if decoded_token["expires"] >= time() else None


if __name__ == "__main__":
    import os
    import binascii

    # Generate secret
    print(binascii.hexlify(os.urandom(24)))

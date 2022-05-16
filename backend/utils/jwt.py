from time import time
from typing import Dict
from .settings import settings

import jwt


def sign_jwt(data: dict, expires: int = 600) -> Dict[str, str]:
    payload = {"data": data, "expires": time() + expires}
    token = jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)

    return {"token": token}


def decode_jwt(token: str) -> dict:
    try:
        decoded_token = jwt.decode(
            token, settings.jwt_secret, algorithms=[settings.jwt_algorithm]
        )
        return decoded_token["data"] if decoded_token["expires"] >= time() else None
    except:
        return {}


if __name__ == "__main__":
    import os
    import binascii

    # Generate secret
    print(str(binascii.hexlify(os.urandom(24))))

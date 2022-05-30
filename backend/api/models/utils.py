from requests import Response

from .response import ApiException, ApiResponse
from .data import Error


def build_error(resp: Response) -> Error:
    """Generate Error from zain-backend failed response"""
    json = resp.json()
    return Error(
        type="zend",
        code=json.get("error").get("code"),
        message=json.get("error").get("message"),
        extra=json.get("extra"),
    )


def build_exception(resp: Response) -> ApiException:
    """Generate ApiException from zain-backend failed response"""
    return ApiException(status_code=resp.status_code, error=build_error(resp))


def build_response(resp: Response) -> ApiResponse:
    """Generate ApiResponse from zain-backend successful response"""
    json = resp.json()
    return ApiResponse(
        status=json.get("status"),
        data=json.get("data"),
        meta=json.get("meta"),
    )

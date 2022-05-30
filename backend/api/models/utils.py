from requests import Response

from .response import ApiException, ApiResponse
from .data import Error


def build_error(resp: Response) -> Error:
    """Generate Error from zain-backend failed response"""
    return Error(
        type="zend",
        code=resp.status_code,
        message=resp.json().get("error").get("message"),
        extra={resp.json().get("extra")},
    )


def build_exception(resp: Response) -> ApiException:
    """Generate ApiException from zain-backend failed response"""
    return ApiException(status=resp.status_code, error=build_error(resp))


def build_response(resp: Response) -> ApiResponse:
    """Generate ApiResponse from zain-backend successful response"""
    return ApiResponse(
        status=resp.json().get("status"),
        data=resp.json().get("data"),
        meta=resp.json().get("meta"),
    )

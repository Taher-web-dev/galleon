from requests import Response

from .response import ApiException, ApiResponse
from .data import Error


def error_obj(resp: Response) -> Error:
    """Generate Error from zain-backend failed response"""
    json = resp.json()
    return Error(
        type="zend",
        code=json.get("error").get("code"),
        message=json.get("error").get("message"),
        extra=json.get("extra"),
    )


def api_exception(resp: Response) -> ApiException:
    """Generate ApiException from zain-backend failed response"""
    return ApiException(status_code=resp.status_code, error=error_obj(resp))


def api_response(resp: Response) -> ApiResponse:
    """Generate ApiResponse from zain-backend successful response"""
    json = resp.json()
    return ApiResponse(
        status=json.get("status"),
        success=json.get("success"),
        data=json.get("data"),
    )

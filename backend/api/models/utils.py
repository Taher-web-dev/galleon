from requests import Response

from .response import ApiException, ApiResponse
from .data import Error, Success


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


def api_response(resp: Response, klass=None) -> ApiResponse:
    """Generate ApiResponse/its inheritors from zain-backend successful response"""
    if klass and not issubclass(klass, ApiResponse):
        raise TypeError("klass must be ApiResponse")
    json = resp.json()
    print(json.get("success"))
    building_data = {
        "status": json.get("status"),
        "success": Success(**json.get("success")),
        "data": json.get("data"),
    }
    if klass:
        return klass(**building_data)

    return ApiResponse(**building_data)

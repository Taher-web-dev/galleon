from utils.api_responses import ApiResponse


class StatusResponse(ApiResponse):
    class Config:
        schema_extra = {
            "example": {
                "status": "success",
            }
        }

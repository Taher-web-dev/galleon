from pydantic import BaseModel


class Error(BaseModel):
    status: str = "error"
    code: int = 99
    message: str = ""

    class Config:
        schema_extra = {
            "example": {"status": "error", "code": 99, "message": "Api error message"}
        }

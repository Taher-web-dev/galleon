from pydantic import BaseModel, Field


class Confirmation(BaseModel):
    confirmation: str = Field(..., example="fjuGQYmZvCBsQbEZ")

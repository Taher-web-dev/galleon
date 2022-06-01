from pydantic import Field
from pydantic.main import BaseModel

class Subaccount(BaseModel):
    account_type: int = Field(..., example=4425)
    amount: int = Field(..., example=30)
    expiry_date: str = Field(..., example="2037-01-01T00:00:00")



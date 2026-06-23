from pydantic import BaseModel, Field

class AccountCreate(BaseModel):
    name: str
    balance: float = Field(ge=1000)



class AmountRequest(BaseModel):
    amount: float = Field(gt=0)


class TransferRequest(BaseModel):
    dest: int
    amount: float = Field(gt=0)
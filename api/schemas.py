from pydantic import BaseModel

class AccountCreate(BaseModel):
    name: str
    balance: float



class AmountRequest(BaseModel):
    amount: float


class TransferRequest(BaseModel):
        dest: int
        amount: float
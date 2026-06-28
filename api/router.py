from typing import Any

from fastapi import FastAPI, HTTPException
from passlib.context import CryptContext
try:
    from .bank import Bank
    from .schemas import AccountCreate, AmountRequest, TransferRequest, UserCreate
except ImportError:  # pragma: no cover - fallback for direct script execution
    from bank import Bank
    from schemas import AccountCreate, AmountRequest, TransferRequest, UserCreate


bank_app = Bank()
app = FastAPI()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")



@app.post("/register")
def register_user(account: AccountCreate, user: UserCreate) -> dict[str, Any]:
    acc = bank_app.create_account(
        account.name,
        account.balance
    )

    if not acc:
        raise HTTPException(
            status_code=500,
            detail="Account Creation Failed"
        )
    

    hashed_password = pwd_context.hash(user.password)
    success = bank_app.db.insert_user(user.username, hashed_password)


    if not success:
        raise HTTPException(
            status_code=400,
            detail="Username already exists"
        )
    


    return {

        "message": f"User {user.username} registered successfully",
        "account_number": acc.account_number,
        "holder": acc.account_holder,
        "balance": acc.balance
    }



@app.post("/login")
def login_user(user: UserCreate) -> dict[str, Any]:

    db_user = bank_app.db.get_user_by_username(user.username)
    if not db_user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    if not pwd_context.verify(user.password, db_user["password_hash"]):
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password"
        )

    return {"message": "Login successful! (JWT token coming soon)"}  





@app.get("/accounts/{id}")
def get_account(id: int) -> dict[str, Any]:

    account = bank_app.search_account(id)

    if not account:
        raise HTTPException(
            status_code=404,
            detail="Account not found"
        )
    
    

    return {
        "account_number": account.account_number,
        "holder": account.account_holder,
        "balance": account.balance
    }




@app.get("/accounts")
def get_accounts() -> dict[str, list[dict[str, Any]]]:
    accounts = bank_app.ls_accounts()

    acc_list: list[dict[str, Any]] = []
    for account in accounts:
        acc_list.append(
            {
                "account_number": account.account_number,
                "holder": account.account_holder,
                "balance": account.balance

        }
        )

    return {
        "accounts": acc_list
    }


# delete yet to be created


@app.post("/accounts/{id}/deposit")
def deposit_account(id: int, amount: AmountRequest) -> dict[str, Any]:
    
    account = bank_app.deposit(id, amount.amount)
    if not account:
        raise HTTPException(
            status_code=404,
            detail="Account not found or invalid deposit amount"
        )
    
    return {
        "Message":  "Deposit successful",
        "new_balance": account.balance
    }

@app.post("/accounts/{id}/withdraw")
def withdraw_account(id: int, amount: AmountRequest) -> dict[str, Any]:
    
    account = bank_app.withdraw(id, amount.amount)
    if not account:
        raise HTTPException(
            status_code=404,
            detail="Account not found or invalid withdraw amount"
            )
    
    return {
        "Message":  "Withdraw successful",
        "new_balance": account.balance
    }

@app.post("/accounts/{id}/transfer")
def transfer_account(id: int, transfer: TransferRequest) -> dict[str, Any]:

    xfer = bank_app.manage_transfer(id, transfer.dest, transfer.amount)

    if not xfer:
        raise HTTPException(
            status_code=400,
            detail="Invalid Transfer"
        )

    acc = bank_app.search_account(id)
    if not acc:
        raise HTTPException(
            status_code=404,
            detail="Account not found"
        )

    return {"new_balance": acc.balance}


@app.get("/transactions")
def get_transactions() -> dict[str, list[dict[str, Any]]]:

    transactions = bank_app.ls_transactions()
    

    return{
        "transactions": transactions
    }



@app.delete("/accounts/{id}/archive")
def archive_account(id: int) -> dict[str, Any]:

    archived_acc = bank_app.archive_account(id)

    if archived_acc is None:
        raise HTTPException(
    status_code=404,
    detail="Account not found"
    )

    return {
        "message": "Account archived successfully",
        "account_holder": archived_acc.account_holder,
        "account_number": archived_acc.account_number,
        "balance": archived_acc.balance
    }

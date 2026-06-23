from typing import Any

from fastapi import FastAPI, HTTPException

try:
    from .bank import Bank
    from .schemas import AccountCreate, AmountRequest, TransferRequest
except ImportError:  # pragma: no cover - fallback for direct script execution
    from bank import Bank
    from schemas import AccountCreate, AmountRequest, TransferRequest


bank_app = Bank()
app = FastAPI()


@app.post("/accounts")
def create_account(account: AccountCreate) -> dict[str, Any]:

    acc = bank_app.create_account(
        account.name,
        account.balance
    )

    if not acc:
        raise HTTPException(
            status_code=500,
            detail="Account Creation Failed"
        )
    
    
    return {

        "account_number": acc.account_number,
        "holder": acc.account_holder,
        "balance": acc.balance
    }


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
    
    account = bank_app.search_account(id)
    if not account:
        raise HTTPException(
            status_code=404,
            detail="Account not found"
        )
    
    
    dep = account.deposit(amount.amount)
    if not dep:
        raise HTTPException(
            status_code=400,
            detail="Invalid deposit amount"
        )       
    bank_app.db.update_balance(
        account.balance,
        account.account_number
    )

    bank_app.db.insert_transaction(
        "DEPOSIT",
        amount.amount,
        account.account_number,
        None
    )
    return {
        "Message":  "Deposit successful",
        "new_balance": account.balance
    }

@app.post("/accounts/{id}/withdraw")
def withdraw_account(id: int, amount: AmountRequest) -> dict[str, Any]:
    
    account = bank_app.search_account(id)
    if not account:
        raise HTTPException(
            status_code=404,
            detail="Account not found"
            )
    widr = account.withdraw(amount.amount)
    if not widr:
        raise HTTPException(
            status_code=400,
            detail="Invalid Withdraw"
        )
    
    bank_app.db.update_balance(
        account.balance,
        account.account_number
    )

    bank_app.db.insert_transaction(
        "WITHDRAW",
        amount.amount,
        account.account_number,
        None
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

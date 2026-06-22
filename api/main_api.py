
from bank import Bank
from fastapi import FastAPI, HTTPException
from schemas import AccountCreate, AmountRequest, TransferRequest


bank_app = Bank()
app = FastAPI()


@app.post("/accounts")
def create_account(account: AccountCreate):

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
def get_account(id: int):

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
def get_accounts():
    accounts = bank_app.ls_accounts()

    acc_list = []
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
def deposit_account(id: int, amount: AmountRequest):
    
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
        "DONE": dep
    }

@app.post("/accounts/{id}/withdraw")
def withdraw_account(id: int, amount: AmountRequest):
    
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
        "DONE": widr
    }

@app.post("/accounts/{id}/transfer")
def transfer_account(id: int, transfer: TransferRequest):

    xfer = bank_app.manage_transfer(id, transfer.dest, transfer.amount)

    if not xfer:
        raise HTTPException(
            status_code=404,
            detail="Invalid Transfer"
        )

    acc = bank_app.search_account(id)
    if not acc:
        raise HTTPException(
            status_code=404,
            detail="Account not found"
        )
    bank_app.db.insert_transaction(
        "TRANSFER",
        transfer.amount,
        id,
        transfer.dest
    )
    return {"new_balance": acc.balance}


@app.get("/transactions")
def get_transactions():

    transactions = bank_app.ls_transactions()
    

    return{
        "transactions": transactions
    }
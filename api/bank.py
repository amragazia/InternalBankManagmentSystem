from __future__ import annotations

from typing import Any

try:
    from .database import DataBase
except ImportError:  # pragma: no cover - fallback for direct script execution
    from database import DataBase


class Account:
    def __init__(self, account_holder: str, account_number: int, balance: float | int | str) -> None:
        self.account_holder: str = account_holder
        self.account_number: int = account_number
        self.balance: float = float(balance)

    def check_balance(self) -> float:
        return self.balance


class Bank:
    def __init__(self) -> None:
        self.db = DataBase()
        self.db.create_tables()

    def create_account(self, account_holder: str, balance: float | int | str) -> Account | None:
        balance = float(balance)
        if balance < 1000:
            return None

        account_number = self.db.get_next_account_number()
        account = Account(account_holder, account_number, balance)
        self.db.insert_account(account)
        return account

    def search_account(self, account_to_be_searched: int) -> Account | None:
        row = self.db.get_account(account_to_be_searched)

        if row is None:
            return None

        return Account(row[1], row[0], row[2])

    def archive_account(self, account_to_be_archived: int) -> Account | None:
        account = self.search_account(account_to_be_archived)

        if account is None:
            return None

        self.db.update_acc_status("ARCHIVED", account_to_be_archived)
        return account

    def manage_transfer(self, source_account: int, destination_account: int, amount: float | int | str) -> bool:
        src = self.search_account(source_account)
        dest = self.search_account(destination_account)

        if src is None or dest is None:
            return False
        if source_account == destination_account:
            return False

        amount = float(amount)
        if not 0 < amount <= src.balance:
            return False

        new_src_balance = src.balance - amount
        new_dest_balance = dest.balance + amount

        success = self.db.execute_atomic_transfer(
            src.account_number,
            dest.account_number,
            new_src_balance,
            new_dest_balance,
            amount,
        )

        if success:
            src.balance = new_src_balance
            dest.balance = new_dest_balance
            return True

        return False

    def deposit(self, account_id: int,amount: float | int | str) -> Account | None:
        account = self.search_account(account_id)
        if account is None:
            return None
        amount = float(amount)
        if amount <= 0:
            return None
        
        new_balance = account.balance + amount
        success = self.db.execute_atomic_single_transaction(
            account_number=account.account_number,
            new_balance=new_balance,
            transaction_type="DEPOSIT",
            amount=amount
        )

        if success:
            account.balance = new_balance
            return account
        return None
        
    def withdraw(self, account_id: int,amount: float | int | str) -> Account | None:
            account = self.search_account(account_id)
            if account is None:
                return None
            
            amount = float(amount)
            if amount > account.balance or amount < 10:               
                return None
            
            new_balance = account.balance - amount

            success = self.db.execute_atomic_single_transaction(
                account_number=account.account_number,
                new_balance=new_balance,
                transaction_type="WITHDRAW",
                amount=amount
            )

            if success:
                account.balance = new_balance
                return account
            return None

    def ls_accounts(self) -> list[Account]:
        rows = self.db.get_all_accounts()
        accounts: list[Account] = []

        for row in rows:
            accounts.append(Account(row[1], row[0], row[2]))

        return accounts

    def ls_transactions(self) -> list[dict[str, Any]]:
        rows = self.db.get_transactions()
        transactions: list[dict[str, Any]] = []

        for row in rows:
            transactions.append(
                {
                    "type": row[1],
                    "amount": row[2],
                    "source": row[3],
                    "destination": row[4],
                    "timestamp": row[5],
                }
            )

        return transactions

    def __len__(self) -> int:
        return self.db.count_accounts()


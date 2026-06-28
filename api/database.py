
from __future__ import annotations

import sqlite3
from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    try:
        from .bank import Account
    except ImportError:  # pragma: no cover - fallback for direct script execution
        from bank import Account


class DataBase:
    def __init__(self, db_path: str = "bank.db") -> None:
        self.conn = sqlite3.connect(db_path, check_same_thread=False)

        # Row Factory for dict-like access
        self.conn.row_factory = sqlite3.Row

        # Enable foreign key support
        self.conn.execute("PRAGMA foreign_keys = ON")  


    def create_tables(self) -> None:
        with self.conn:
            self.conn.execute(
                """
            CREATE TABLE IF NOT EXISTS accounts(
                account_number INTEGER PRIMARY KEY,
                account_holder TEXT NOT NULL,
                balance REAL NOT NULL,
                status TEXT NOT NULL,
                user_id INTEGER NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
            """
            )

            self.conn.execute(
                """
            CREATE TABLE IF NOT EXISTS transactions(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                transaction_type TEXT NOT NULL,
                amount REAL NOT NULL,
                source_account INTEGER,
                destination_account INTEGER,
                timestamp TEXT NOT NULL
            )
            """
            )

            self.conn.execute(
                """
            CREATE TABLE IF NOT EXISTS users(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL
            )
            """
            )


    def get_next_user_id(self) -> int:
        cur = self.conn.cursor()
        cur.execute(
            """
            SELECT MAX(id)
            FROM users
            """
        )
        result = cur.fetchone()
        cur.close()

        if result is None:
            return 1

        max_user_id = result[0]
        return 1 if max_user_id is None else int(max_user_id) + 1
    

    def insert_user(self, username: str, password_hash: str) -> bool:
        try:
            with self.conn:
                self.conn.execute(
                    """
                INSERT INTO users (username, password_hash)
                VALUES (?, ?)
                """,
                (username, password_hash),
            )
                
            return True
        except sqlite3.IntegrityError:
            return False  # Username already exists
        


    def get_user_by_username(self, username: str) -> sqlite3.Row | None:
        cur = self.conn.cursor()
        cur.execute(
            """
            SELECT *
            FROM users
            WHERE username = ?
            """,
            (username,),
        )
        result = cur.fetchone()
        cur.close()
        return result


    def get_next_account_number(self) -> int:
        cur = self.conn.cursor()
        cur.execute(
            """
        SELECT MAX(account_number)
        FROM accounts
        """
        )

        result = cur.fetchone()
        cur.close()

        if result is None:
            return 1001

        max_account_number = result[0]
        return 1001 if max_account_number is None else int(max_account_number) + 1

    def get_account(self, account_number: int) -> sqlite3.Row | None:
        cur = self.conn.cursor()
        cur.execute(
            """
            SELECT account_number,account_holder,balance
            FROM accounts
            WHERE account_number = ? AND status = 'ACTIVE'
            """,
            (account_number,),
        )
        result = cur.fetchone()
        cur.close()
        return result

    def insert_account(self, account: Account, user_id: int) -> None:
        with self.conn:
            self.conn.execute(
                """
            INSERT INTO accounts
            (account_number, account_holder, balance, status, user_id)
            VALUES (?, ?, ?, ?, ?)
            """,
                (account.account_number, account.account_holder, account.balance, "ACTIVE", user_id),
            )

    def update_acc_status(self, status: str, account_number: int) -> None:
        with self.conn:
            self.conn.execute(
                """
            UPDATE accounts
            SET status = ?
            WHERE account_number = ?
            """,
                (status, account_number),
            )

    def execute_atomic_transfer(
        self,
        src_acc_num: int,
        dest_acc_num: int,
        src_new_bal: float,
        dest_new_bal: float,
        amount: float,
    ) -> bool:
        timestamp = datetime.now().isoformat()

        try:
            with self.conn:
                self.conn.execute(
                    """
                UPDATE accounts SET balance = ? WHERE account_number = ?
                """,
                    (src_new_bal, src_acc_num),
                )
                self.conn.execute(
                    """
                UPDATE accounts SET balance = ? WHERE account_number = ?
                """,
                    (dest_new_bal, dest_acc_num),
                )

                self.conn.execute(
                    """
                INSERT INTO transactions
                (transaction_type, amount, source_account, destination_account, timestamp)
                VALUES (?, ?, ?, ?, ?)
                """,
                    ("TRANSFER", amount, src_acc_num, dest_acc_num, timestamp),
                )

            return True

        except sqlite3.Error as e:
            print(f"Transaction failed: {e}")
            return False


    def get_transactions(self) -> list[sqlite3.Row]:
        cur = self.conn.cursor()
        cur.execute(
            """
        SELECT *
        FROM transactions
        ORDER BY id DESC
        """
        )
        result = cur.fetchall()
        cur.close()
        return result

    def get_all_accounts(self) -> list[sqlite3.Row]:
        cur = self.conn.cursor()
        cur.execute(
            """
        SELECT account_number,
               account_holder,
               balance
        FROM accounts
        WHERE status = 'ACTIVE'
        """
        )
        result = cur.fetchall()
        cur.close()
        return result

    def count_accounts(self) -> int:
        cur = self.conn.cursor()

        cur.execute(
            """
        SELECT COUNT(*)
        FROM accounts
        WHERE status = 'ACTIVE'
        """
        )
        result = cur.fetchone()[0]
        cur.close()
        return int(result)

    def update_balance(self, balance: float, account_number: int) -> None:
        with self.conn:
            self.conn.execute(
                """
            UPDATE accounts
            SET balance = ?
            WHERE account_number = ?
            """,
                (balance, account_number),
            )

    def insert_transaction(
        self,
        transaction_type: str,
        amount: float,
        src: int | None,
        dest: int | None,
    ) -> None:
        timestamp = datetime.now().isoformat()
        with self.conn:
            self.conn.execute(
                """
            INSERT INTO transactions
            (
                transaction_type,
                amount,
                source_account,
                destination_account,
                timestamp
            )
            VALUES (?, ?, ?, ?, ?)
            """,
                (transaction_type, amount, src, dest, timestamp),
            )


    def execute_atomic_single_transaction(
            self, 
            account_number: int, 
            new_balance: float, 
            transaction_type: str, 
            amount: float
        ) -> bool:
            timestamp = datetime.now().isoformat()

            try:
                # The 'with' block ensures both queries succeed, or both rollback
                with self.conn:
                    self.conn.execute(
                        """
                        UPDATE accounts SET balance = ? WHERE account_number = ?
                        """,
                        (new_balance, account_number),
                    )

                    self.conn.execute(
                        """
                        INSERT INTO transactions
                        (transaction_type, amount, source_account, destination_account, timestamp)
                        VALUES (?, ?, ?, ?, ?)
                        """,
                        (transaction_type, amount, account_number, None, timestamp),
                    )

                return True

            except sqlite3.Error as e:
                print(f"Transaction failed: {e}")
                return False





    def close(self) -> None:
        self.conn.close()


import sqlite3
from datetime import datetime

class DataBase:

    def __init__(self):
        self.conn = sqlite3.connect(
            "bank.db",
             check_same_thread=False
           )


    def create_tables(self):
        with self.conn:
            self.conn.execute("""
            CREATE TABLE IF NOT EXISTS accounts(
                account_number INTEGER PRIMARY KEY,
                account_holder TEXT NOT NULL,
                balance REAL NOT NULL,
                status TEXT NOT NULL 
            )
            """)
            
            self.conn.execute("""
            CREATE TABLE IF NOT EXISTS transactions(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                transaction_type TEXT NOT NULL,
                amount REAL NOT NULL,
                source_account INTEGER,
                destination_account INTEGER,
                timestamp TEXT NOT NULL
            )
            """)


    
    def get_next_account_number(self):
        cur = self.conn.cursor()
        cur.execute("""
        SELECT MAX(account_number)
        FROM accounts
        """)

        result = cur.fetchone()
        cur.close()

        return 1001 if result[0] is None else result[0] + 1
    
    def get_account(self, account_number):
        cur = self.conn.cursor()
        cur.execute("""
            SELECT account_number,account_holder,balance
            FROM accounts
            WHERE account_number = ? AND status = 'ACTIVE'
            """, (account_number,))
        result = cur.fetchone()
        cur.close()
        return result
    

    def insert_account(self, account):
        
        with self.conn:
            self.conn.execute("""
            INSERT INTO accounts
            (account_number, account_holder, balance, status)
            VALUES (?, ?, ?, ?)
            """, 
            (
                account.account_number,
                account.account_holder,
                account.balance,
                "ACTIVE"
            ))



    def update_acc_status(self, status, account_number):
        with self.conn:
            self.conn.execute("""
            UPDATE accounts
            SET status = ?
            WHERE account_number = ?
            """, (status, account_number))



    def execute_atomic_transfer(
        self, src_acc_num, dest_acc_num, src_new_bal, dest_new_bal, amount
            ):
        
        timestamp = datetime.now().isoformat()

        try:
            with self.conn:
                self.conn.execute("""
                UPDATE accounts SET balance = ? WHERE account_number = ?
                """, (src_new_bal, src_acc_num))
                self.conn.execute("""
                UPDATE accounts SET balance = ? WHERE account_number = ?
                """, (dest_new_bal, dest_acc_num))

                self.conn.execute("""
                INSERT INTO transactions 
                (transaction_type, amount, source_account, destination_account, timestamp)
                VALUES (?, ?, ?, ?, ?)
                """, ("TRANSFER", amount, src_acc_num, dest_acc_num, timestamp))

            return True
        
        except sqlite3.Error as e:
            print(f"Transaction failed: {e}")
            return False

    def insert_transaction(self, transaction_type, amount, src, dest):
        timestamp = datetime.now().isoformat()
        with self.conn:
            self.conn.execute("""
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
            (
                transaction_type,
                amount,
                src,
                dest,
                timestamp
            ))
    
    def get_transactions(self):
        cur = self.conn.cursor()
        cur.execute("""
        SELECT *
        FROM transactions
        ORDER BY id DESC
        """)
        result = cur.fetchall()
        cur.close()
        return result
    
    def get_all_accounts(self):
        cur = self.conn.cursor()
        cur.execute("""

        SELECT account_number,
               account_holder,
               balance       
        FROM accounts
        WHERE status = 'ACTIVE'
        """)
        result = cur.fetchall()
        cur.close()
        return result


    def count_accounts(self):
        cur = self.conn.cursor()

        cur.execute("""
        SELECT COUNT(*)
        FROM accounts
        WHERE status = 'ACTIVE'

        """)
        result = cur.fetchone()[0]
        cur.close()
        return result
    

    def update_balance(self, balance, account_number):
        with self.conn:
            self.conn.execute("""
            UPDATE accounts
            SET balance = ?
            WHERE account_number = ?
            """, (balance, account_number)       
            )

    def close(self):
        self.conn.close()

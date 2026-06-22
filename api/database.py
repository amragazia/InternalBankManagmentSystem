import sqlite3
from datetime import datetime

class DataBase:

    def __init__(self):
        self.conn = sqlite3.connect(
            "bank.db",
             check_same_thread=False
           )
        self.cur = self.conn.cursor()


    def create_tables(self):
        self.cur.execute("""
        CREATE TABLE IF NOT EXISTS accounts(
            account_number INTEGER PRIMARY KEY,
            account_holder TEXT NOT NULL,
            balance REAL NOT NULL,
            status TEXT NOT NULL 
            )
            """)
        
        self.cur.execute("""
        CREATE TABLE IF NOT EXISTS transactions(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            transaction_type TEXT NOT NULL,
            amount REAL NOT NULL,
            source_account INTEGER,
            destination_account INTEGER,
            timestamp TEXT NOT NULL
            )
             """)
        
        self.conn.commit()


        


    
    def get_next_account_number(self):

        self.cur.execute("""
        SELECT MAX(account_number)
        FROM accounts
        """)

        result = self.cur.fetchone()

        if result[0] is None:
            return 1001
        return result[0] + 1
    
    def get_account(self, account_number):
        self.cur.execute("""
            SELECT account_number,
                   account_holder,
                   balance
        FROM accounts
        WHERE account_number = ?
        AND status = 'ACTIVE'
        """, (account_number,))
    
        return self.cur.fetchone()
    

    def insert_account(self, account):

        self.cur.execute("""
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
        self.conn.commit()



    def insert_transaction(self, transaction_type, amount, src, dest):

        timestamp = datetime.now().isoformat()

        self.cur.execute("""
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
        self.conn.commit()

    
    def get_transactions(self):
        self.cur.execute("""
        SELECT *
        FROM transactions
        ORDER BY id DESC
        """)
        return self.cur.fetchall()

    def archive_account(self, account_number):

        self.cur.execute("""
        UPDATE accounts
        SET status = 'ARCHIVED'
        WHERE account_number = ?
        """, (account_number,))

        self.conn.commit()

    def get_all_accounts(self):

        self.cur.execute("""

        SELECT account_number,
               account_holder,
               balance       
        FROM accounts
        WHERE status = 'ACTIVE'
        """)

        return self.cur.fetchall()


    def count_accounts(self):

        self.cur.execute("""
        SELECT COUNT(*)
        FROM accounts
        WHERE status = 'ACTIVE'

        """)

        return self.cur.fetchone()[0]
    

    def update_balance(self, balance, account_number):

        self.cur.execute("""

        UPDATE accounts
        SET balance = ?
        WHERE account_number = ?
       """, (balance, account_number)       
       )


        self.conn.commit()

    def close(self):
        self.conn.close()
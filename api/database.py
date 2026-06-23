import sqlite3
from datetime import datetime

class DataBase:

    def __init__(self):
        self.conn = sqlite3.connect(
            "bank.db",
             check_same_thread=False
           )


    def create_tables(self):
        cur = self.conn.cursor()
        cur.execute("""
        CREATE TABLE IF NOT EXISTS accounts(
            account_number INTEGER PRIMARY KEY,
            account_holder TEXT NOT NULL,
            balance REAL NOT NULL,
            status TEXT NOT NULL 
            )
            """)
        
        cur.execute("""
        CREATE TABLE IF NOT EXISTS transactions(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            transaction_type TEXT NOT NULL,
            amount REAL NOT NULL,
            source_account INTEGER,
            destination_account INTEGER,
            timestamp TEXT NOT NULL
            )
             """)
        cur.close()
        self.conn.commit()


        


    
    def get_next_account_number(self):
        cur = self.conn.cursor()

        cur.execute("""
        SELECT MAX(account_number)
        FROM accounts
        """)

        result = cur.fetchone()
        cur = self.conn.cursor()

        if result[0] is None:
            return 1001
        return result[0] + 1
    
    def get_account(self, account_number):
        cur = self.conn.cursor()

        cur.execute("""
            SELECT account_number,
                   account_holder,
                   balance
        FROM accounts
        WHERE account_number = ?
        AND status = 'ACTIVE'
        """, (account_number,))
        cur.close()
        return cur.fetchone()
    

    def insert_account(self, account):
        cur = self.conn.cursor()

        cur.execute("""
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
        cur.close()
        self.conn.commit()


    def update_acc_status_when_archived(self, status, account_number):
        cur = self.conn.cursor()

        cur.execute("""
        UPDATE accounts
        SET status = ?
        WHERE account_number = ?
        """, (status, account_number))
        cur.close()
        self.conn.commit()



    def execute_atomic_transfer(
        self, src_acc_num, dest_acc_num, src_new_bal, dest_new_bal, amount
            ):
        
        cur = self.conn.cursor()
        timestamp = datetime.now().isoformat()

        try:
            cur.execute("""
            UPDATE accounts SET balance = ? WHERE account_number = ?
            """, (src_new_bal, src_acc_num))
            cur.execute("""
            UPDATE accounts SET balance = ? WHERE account_number = ?
            """, (dest_new_bal, dest_acc_num))

            cur.execute("""
            INSERT INTO transactions 
            (transaction_type, amount, source_account, destination_account, timestamp)
            VALUES (?, ?, ?, ?, ?)
            """, ("TRANSFER", amount, src_acc_num, dest_acc_num, timestamp))

            self.conn.commit()
            return True
        
        except sqlite3.Error as e:
            self.conn.rollback()
            print(f"Transaction failed: {e}")
            return False
        
        finally:
            cur.close()


    def insert_transaction(self, transaction_type, amount, src, dest):

        timestamp = datetime.now().isoformat()
        
        cur = self.conn.cursor()
        cur.execute("""
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
        cur.close()
        self.conn.commit()

    
    def get_transactions(self):
        cur = self.conn.cursor()
        cur.execute("""
        SELECT *
        FROM transactions
        ORDER BY id DESC
        """)
        cur.close()
        return cur.fetchall()

    def archive_account(self, account_number):
        cur = self.conn.cursor()
        cur.execute("""
        UPDATE accounts
        SET status = 'ARCHIVED'
        WHERE account_number = ?
        """, (account_number,))
        cur.close()
        self.conn.commit()

    def get_all_accounts(self):
        cur = self.conn.cursor()
        cur.execute("""

        SELECT account_number,
               account_holder,
               balance       
        FROM accounts
        WHERE status = 'ACTIVE'
        """)
        cur.close()
        return cur.fetchall()


    def count_accounts(self):
        cur = self.conn.cursor()

        cur.execute("""
        SELECT COUNT(*)
        FROM accounts
        WHERE status = 'ACTIVE'

        """)
        cur.close()
        return cur.fetchone()[0]
    

    def update_balance(self, balance, account_number):
        cur = self.conn.cursor()
        cur.execute("""

        UPDATE accounts
        SET balance = ?
        WHERE account_number = ?
       """, (balance, account_number)       
       )

        cur.close()
        self.conn.commit()

    def close(self):
        self.conn.close()

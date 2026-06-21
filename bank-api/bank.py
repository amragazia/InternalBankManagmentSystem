
from database import DataBase
class Account:
    def __init__(self, account_holder, account_number, balance):

        self.account_holder = account_holder
        self.account_number = account_number
        self.balance = balance
        

    def deposit(self, amount):
        if 0 >= amount:
            return False

        self.balance += amount
        return True

    def withdraw(self, amount):
        if amount > self.balance:
            return False
        if 10 > amount:
            return False
        
        self.balance -= amount
        return True
    
    def transfer_request(self, destination_account, amount): #transfer request to bank
        if not 0 < amount <= self.balance:
            return False
        return self.account_number, destination_account, amount

    def check_balance(self):
        return self.balance
    

class Bank:


    def __init__(self):
        self.db = DataBase()
        self.db.create_tables()

    def create_account(self, account_holder, balance):
        if not 1000 <= balance:
            return None
        account_number = self.db.get_next_account_number()
        
        account = Account(
            account_holder,
            account_number,
            balance
        )

        self.db.insert_account(account)
    
        return account
    
    def search_account(self, account_to_be_searched):
        
        row = self.db.get_account(account_to_be_searched)

        if row is None:
            return None


        return Account(
            row[1],
            row[0],
            row[2]
        )

    def archive_account(self, account_to_be_archived):  # when cx requests to cancel service and delete account, we archive it

        account = self.search_account(account_to_be_archived)

        if account is None:
            return None
  
        self.db.archive_account(account_to_be_archived)
        return account

    def manage_transfer(self, source_account, destination_account, amount):
        src = self.search_account(source_account)
        dest = self.search_account(destination_account)
        if (src is None or dest is None):
            return False
        if source_account == destination_account:
            return False
        if not src.withdraw(amount):
            return False
        if not dest.deposit(amount):
            src.deposit(amount)   # rollback
            return False
        
        self.db.update_balance(
            src.balance,
            src.account_number
        )
        self.db.update_balance(
            dest.balance,
            dest.account_number
        )
        return True
    
    def ls_accounts(self): 
        rows = self.db.get_all_accounts()
        accounts = []

        for row in rows:
            accounts.append(
                Account(
                    row[1],
                    row[0],
                    row[2]
                )
            )

        return accounts

    def ls_transactions(self):
        return self.db.get_transactions()
            

    def __len__(self):
        return self.db.count_accounts()


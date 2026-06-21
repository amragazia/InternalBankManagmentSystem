# Internal Bank Management System, Authorized Use Only

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
        self.transactions = []


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
            row[0],
            row[1],
            row[2]
        )

    def archive_account(self, account_to_be_archived):  # when cx requests to cancel service and delete account, we archive it

        account = self.search_account(account_to_be_archived)

        if account is None:
            return None
        
        self.archived.append(account)
        self.accounts.remove(account)
        return account

    def manage_transfer(self, source_account, destination_account, amount):
        src = self.search_account(source_account)
        dest = self.search_account(destination_account)
        if (src is None or dest is None):
            return False
        if src == dest:
            return False
        if not src.withdraw(amount):
            return False
        if not dest.deposit(amount):
            src.deposit(amount)   # rollback
            return False
        return True
    
    def ls_accounts(self): 
        return self.accounts.copy()
    

    def ls_transactions(self):
        return self.transactions.copy()
            

    def __len__(self):
        return len(self.accounts)





def validate_name(name):
    name = name.strip()

    if not (2 <= len(name) <= 50):
        return False

    if not any(char.isalpha() for char in name):
        return False

    for char in name:
        if not (char.isalpha() or char in " -'"):
            return False

    return True


def get_amount(prompt):
    while True:
        amount  = input(prompt).strip()
        if not amount.isdigit():
            print("Amount must be numeric.")
            continue
        return int(amount)    
    

def get_account_number():
    while True:
        acc_num = input("> Enter Account Number: ").strip()
        if not acc_num.isdigit():
            print("Invalid Entry")
            continue
        acc_num  = int(acc_num)
        if acc_num < 1001:
            print("Invalid Entry")
            continue
        return acc_num

# application/controller layer.
def main(): 
    bank = Bank()
    while True:
        print("Main Menu:")
        print("1-Access Account")
        print("2-Create Account")
        print("3-Search Account")
        print("4-Archive Account")
        print("5-List Accounts(Detailed)")
        print("6-List Number Of Accounts")
        print("7-List Transaction")  
        print("8-Exit") 
        while True:
            choice = input("> ").strip()
            if choice not in ["1", "2", "3", "4", "5", "6", "7", "8"]:
                print("Invalid Entry")
                continue
            break


        if choice == "1":

            acc_num = get_account_number()
            account = bank.search_account(acc_num)

            if not account:
                print("Account does not exist.")
                continue

            print(f">Account: {account.account_number}")

            while True:
                print("Account Menu:")
                print("1-Deposit Money")
                print("2-Withdraw Money")
                print("3-transfer Money")
                print("4-Check Balance")
                print("5-Exit") 
                while True:
                    do = input("> ").strip()
                    if do not in ["1", "2", "3", "4", "5"]:
                        print("Invalid Entry")
                        continue
                    break

                if do == "1":
                    amount = get_amount("Enter Amount To Deposit: ")
                    if not account.deposit(amount):
                        print("Invalid Deposit")
                        continue
                    print("Deposit successful.")
                    bank.transactions.append({
                        "type": "DEPOSIT",
                        "amount": amount,
                        "source": account.account_number,
                        "destination": None
                    })
                elif do == "2":
                    amount = get_amount("Enter Amount To Withdraw: ")
                    if not account.withdraw(amount):
                        print("Invalid Withdrawal")
                        continue
                    print("Withdraw successful.")

                    bank.transactions.append({
                        "type": "WITHDRAW",
                        "amount": amount,
                        "source": account.account_number,
                        "destination": None
                    })                    


                elif do == "3":
                    amount = get_amount("Enter Amount To Transfer: ")
                    dest_acc_num = input("> Enter Account Number: ").strip()
                    if not dest_acc_num.isdigit():
                        print("Invalid Entry")
                        continue
                    dest_acc_num = int(dest_acc_num)
                    
                    request = account.transfer_request(dest_acc_num, amount)
                    if not request:
                        print("Invalid Transfer.")
                        continue
                    else:
                        src, dest, amount = request
                        xfer = bank.manage_transfer(src, dest, amount)
                        if not xfer:
                            print("Invalid Transfer.")
                            continue
                        else: 
                            print("Transferred Successfully!")
                            print(f"New balance is {account.check_balance()}")


                    bank.transactions.append({
                        "type": "TRANSFER",
                        "amount": amount,
                        "source": src,
                        "destination": dest
                    })             

                elif do == "4":
                    balance = account.check_balance()
                    print(f"Your Available Balance is {balance}")

                elif do == "5":
                    break

            continue        

            


        elif choice == "2":
            
            while True:
                acc_holder_name = input(">Enter Your Name: ")
                if not validate_name(acc_holder_name):
                    print("Invalid Name")
                    continue
                balance = input("> Enter Your Opening Balance: ").strip()
                if not balance.isdigit():
                    print("Balance must be numeric.")
                    continue
                balance = int(balance)
                break

            acc_created = bank.create_account(acc_holder_name, balance)
            if not acc_created:
                print("Account Opening Failed!")
                continue
            print(f"Account Created Successfully")
            print("*" * 20)
            print(f"Account Holder: {acc_created.account_holder}")
            print(f"Account Number: {acc_created.account_number}")
            print(f"Balance: {acc_created.balance}")

            bank.transactions.append({
                "type": "ACCOUNT_CREATED",
                "amount": balance,
                "source": acc_created.account_number,
                "destination": None
            })
            continue

        elif choice == "3":
            acc_num = get_account_number()
            account = bank.search_account(acc_num)

            if not account:
                print("Account does not exist.")
                continue

            print("Account Found")
            print("*" * 20)
            print(f"Account Holder: {account.account_holder}")
            print(f"Account Number: {account.account_number}")
            print(f"Balance: {account.balance}")
            
            continue

        elif choice == "4":
            acc_num = get_account_number()
            archived_acc = bank.archive_account(acc_num)
            if archived_acc is None:
                print("Archive failed!")
                continue

            print(f"{archived_acc.account_number} has been archived.")
            continue


        elif choice == "5":
            accounts = bank.ls_accounts()
            if not accounts:
                print("No active accounts.")
                continue
            for acc in accounts:
                print("-" * 25)
                print(f"Account Holder: {acc.account_holder}")
                print(f"Account Number: {acc.account_number}")
                print(f"Balance: {acc.balance}")
                    
            
            print("-" * 25)


        elif choice == "6":
            print(len(bank))
            continue

        elif choice == "7":
            transactions = bank.ls_transactions()
            if not transactions:
                print("No logged transactions.")
                continue
            for transaction in transactions:
                print("-" * 25)
                for key, val in transaction.items():
                    print(f"{key} : {val}")

            
            print("-" * 25)
        
        elif choice == "8":
            break



main()
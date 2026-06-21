# Internal Bank Management System, Authorized Use Only
from bank import Bank

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
    bank_app = Bank()
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
            account = bank_app.search_account(acc_num)

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
                    bank_app.db.update_balance(
                        account.balance,
                        account.account_number
                    )

                    bank_app.db.insert_transaction(
                        "DEPOSIT",
                        amount,
                        account.account_number,
                        None
                    )

                elif do == "2":
                    amount = get_amount("Enter Amount To Withdraw: ")
                    if not account.withdraw(amount):
                        print("Invalid Withdrawal")
                        continue
                    print("Withdraw successful.")
                    bank_app.db.update_balance(
                        account.balance,
                        account.account_number
                    )

                    bank_app.db.insert_transaction(
                        "WITHDRAW",
                        amount,
                        account.account_number,
                        None
                    )     


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
                        if not bank_app.manage_transfer(src, dest, amount):
                            print("Invalid Transfer.")
                            continue
                        else: 
                            print("Transferred Successfully!")
                            new_balance = bank_app.search_account(src)
                            print(f"New balance is {new_balance.check_balance()}")


                    bank_app.db.insert_transaction(
                        "TRANSFER",
                        amount,
                        src,
                        dest
                    )

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

            acc_created = bank_app.create_account(acc_holder_name, balance)
            if not acc_created:
                print("Account Opening Failed!")
                continue
            print(f"Account Created Successfully")
            print("*" * 20)
            print(f"Account Holder: {acc_created.account_holder}")
            print(f"Account Number: {acc_created.account_number}")
            print(f"Balance: {acc_created.balance}")
            bank_app.db.insert_transaction(
                "ACCOUNT_CREATED",
                acc_created.balance,
                acc_created.account_number,
                None
            )     
            continue

        elif choice == "3":
            acc_num = get_account_number()
            account = bank_app.search_account(acc_num)

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
            archived_acc = bank_app.archive_account(acc_num)
            if archived_acc is None:
                print("Archive failed!")
                continue

            print(f"{archived_acc.account_number} has been archived.")
            continue


        elif choice == "5":
            accounts = bank_app.ls_accounts()
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
            print(len(bank_app))
            continue

        elif choice == "7":
            transactions = bank_app.db.get_transactions()
            if not transactions:
                print("No logged transactions.")
                continue
            for transaction in transactions:
                print("-" * 25)
                print(f"ID: {transaction[0]}")
                print(f"Type: {transaction[1]}")
                print(f"Amount: {transaction[2]}")
                print(f"Source: {transaction[3]}")
                print(f"Destination: {transaction[4]}")
                print(f"Timestamp: {transaction[5]}")

            
            print("-" * 25)
        
        elif choice == "8":
            bank_app.db.close()
            break



if __name__ == "__main__":
    main()
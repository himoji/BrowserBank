'''
Simple console-based ATM programm
with mysql database
poor perfomance, but anyway its iobound
'''



'''
TODO: loan system
check when send money
'''
#import mysql driver and connect to database with (host, user, password and database name) info
import mysql.connector
import getpass

try:
    db = mysql.connector.connect(
        host = 'localhost',
        user = 'root',
        password = 'admin',
        database = 'customers_db'
    )
    #cursor = db.cursor()
    print("Connected successfully")

except Exception as err:
    print("Connection refused\n", err)


def securityCheck(*args) -> bool:
    '''
    Checks user input for: blacklisted words, going out-of-bounds
\n
    returns bool, True = blacklisted words are in input, False = not
    '''
    violated = False
    blacklisted_words = [
        "select",
        "drop",
        "delete",
        "where",
        "insert",
        "commit",
        "rollback",
        ";"
        "from",
        "*",
        "update",
        "()"
                         ]
    
    for word in args:
        if len(word) > 20: 
            violated = True

        if word.lower() in blacklisted_words:
            violated = True

    if violated:
        return True
    return False


class accountManagment:
    def login(customer_name, password) -> str:
        '''
    Login command to take user input and check is it password.\n
    takes 2 args
        '''
        cursor = db.cursor()

        cursor.execute(f'select customer_id from customers_table where customer_name = "{customer_name.lower()}" and customer_password = "{password}";') # type: ignore
        result = cursor.fetchone()
        cursor.close()
        try:
            if isinstance(result[0], int) and securityCheck(customer_name, password)==False:
                return customer_name
        except: pass
        return "no_customer"
      
        
    def changePassword(customer_name, old_password, new_password) -> bool:
        '''
    ChngPass command to take user input and set it as password.\n
    takes 3 args.
        '''
        cursor = db.cursor()

        cursor.execute(f'select customer_id from customers_table where customer_name = "{customer_name.lower()}" and customer_password = "{old_password}";') # type: ignore
        result = cursor.fetchone()

        try: 
            if isinstance(result[0], int) and securityCheck(customer_name, old_password, new_password)==False:
                cursor.execute(f'update customers_table set customer_password = "{new_password}" where customer_name = "{customer_name}";')
                cursor.close()
                db.commit()
                return True 
        except: pass
        return False


    def register(customer_name, password) -> bool:
        '''
    Register command to take user input and load it into customers_table.\n
    takes 2 args, True = success, False = not.
        '''
        cursor = db.cursor()
        try: 
            if securityCheck(customer_name, password)==False:
                cursor.execute(f'insert into customers_table(customer_name, customer_password) values ("{customer_name}", "{password}");')
                cursor.close()
                db.commit()
                return True
        except: pass
        return False

        
    def deleteAcc(customer_name, password) -> bool:
        '''
    Delete command to delete a row with specified id \n
    takes 2 args, True = success , False = not.
        '''

        cursor = db.cursor()
        try: 
            if securityCheck(customer_name, password)==False:
                cursor.execute(f'delete from customers_table where customer_name = "{customer_name}" and customer_password = "{password}";')
                cursor.close()
                db.commit()
                return True
        except: pass
        return False
"""

class atm():
    def getCustomerNameById():
        cursor = db.cursor()
        cursor.execute(f'select customer_name from customers_table where customer_id = {self.current_customer_id};')
        return cursor.fetchone()[0]
    

    def deposit(self) -> None:
        '''
    'Deposit command to update CASH at customer_id.\n
    Cash += cash_input for user.\n
    takes 0 args, only asks inside of function.
    '''
        try:
            cash = int(input('How much do you want to deposit (input integer)?: '))
            if cash < 0:
                print("You cant take debt here!")
                cash = str(cash)
                cash = "nope"
        except:
            print("Deposit Only integers and positive numbers, ATM can not hold cents")

        cursor.execute(f'update customers_table set customer_cash = customer_cash + {cash} where customer_id = "{self.current_customer_id}";') # type: ignore
        self.printCashAmount()


    def withdraw(self) -> None:
        '''
    Withdraw command to update CASH at customer_id.\n
    Cash -= cash_input for user.\n
    takes 0 args, only asks inside of function.
    '''
        try: #check how much money customer have
            cursor.execute(f'select customer_cash from customers_table where customer_id = {self.current_customer_id};')
            result = cursor.fetchone()
        except: pass

        try:
            cash = int(input('How much do you want to withdraw (input integer)?: '))
            if cash < 0 or int(result[0]) - cash < 0: #type: ignore
                print("You cant take debt here!")
                cash = str(cash)
                cash = "nope"
        except:
            print("Withdraw Only integers and positive numbers, ATM can not hold cents")

        cursor.execute(f'update customers_table set customer_cash = customer_cash - {cash} where customer_id = "{self.current_customer_id}";') #type: ignore
        self.printCashAmount()


    def send(self) -> None:
        '''
    Send command to update CASH at customer_id[i] and customer_id[j].\n
    Sends cash from one user to another.\n
    takes 0 args, only asks inside of function.
    '''
        cursor.execute('select customer_name from customers_table;')
        
        for i, name in enumerate(cursor.fetchall(), start=1):
            print(f"{i}) {name}")
        try:
            taker_id = int(input('Send money to who? (taker id): '))
        except: pass

        try: #check how much money customer do have
            cursor.execute(f'select customer_cash from customers_table where customer_id = {self.current_customer_id};')
            cash_on_sender_card = cursor.fetchone()
        except: pass

        try:
            cash_to_send = int(input('How much do you want to withdraw (input integer)?: '))
            if cash_to_send < 0 or int(cash_on_sender_card[0]) - cash_to_send < 0: #type: ignore
                print("You cant take debt here!")
                cash_to_send = str(cash_to_send)
                cash_to_send = "nope"
        except:
            print("Only integers and positive numbers, ATM can not hold cents")

        a = f'update customers_table set customer_cash = customer_cash - {cash_to_send} where customer_id = "{self.current_customer_id}";' # type: ignore
        b = f'update customers_table set customer_cash = customer_cash + {cash_to_send} where customer_id = "{taker_id}";' # type: ignore

        cursor.execute(a)
        cursor.execute(b)

        self.printCashAmount()
        self.printCashAmountById(taker_id) #type: ignore


    def printCashAmountById(current_customer_id) -> None:
        '''
    Select command to print in terminal\n
    Print in terminal amount of money of customer_id \n
    Takes 1 positional arg: customer_id e.g. "1"
    '''
        cursor.execute(f'select customer_cash from customers_table where customer_id = "{current_customer_id}";')

        result = cursor.fetchone()
        print(f"#{current_customer_id}'s cash is now {result[0]}")
        

    def printCashAmount() -> None:
        '''
    Select command to print in terminal\n
    Print in terminal amount of money of customer_id \n
    Takes 1 positional arg: customer_id e.g. "1"
    '''
        cursor.execute(f'select customer_cash from customers_table where customer_id = "{self.current_customer_id}";')

        result = cursor.fetchone()
        print(f"#{self.current_customer_id}'s cash is now {result[0]}")

"""


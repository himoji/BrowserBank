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
import psycopg2
import redis


db = psycopg2.connect(database="db", user="postgres", password="admin", port=13337)
cursor = db.cursor()
print("Connected successfully")


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

        cursor.execute(f"select customer_id from customers_table where customer_name = '{customer_name.lower()}' and customer_password = '{password}';") # type: ignore
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

        cursor.execute(f"select customer_id from customers_table where customer_name = '{customer_name.lower()}' and customer_password = '{old_password}';") # type: ignore
        result = cursor.fetchone()

        try: 
            if isinstance(result[0], int) and securityCheck(customer_name, old_password, new_password)==False:
                cursor.execute(f"update customers_table set customer_password = '{new_password}' where customer_name = '{customer_name}';")
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
                cursor.execute(f"insert into customers_table(customer_name, customer_password) values ('{customer_name}', '{password}');")
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
                cursor.execute(f"delete from customers_table where customer_name = '{customer_name}' and customer_password = '{password}';")
                cursor.close()
                db.commit()
                return True
        except: pass
        return False


class atm():
    def deposit(customer_name, cash) -> bool:
        '''
    'Deposit command to update CASH at customer_id.\n
    Cash += cash_input for user.\n
    takes 0 args, only asks inside of function.
    '''
        cursor = db.cursor()
        try:
            if int(cash) >= 0 and securityCheck(customer_name)==False:
                print("Depositing cash")
                cursor.execute(f"update customers_table set customer_cash = customer_cash + {cash} where customer_name = '{customer_name}';")
                cursor.close()
                db.commit()
                return True
        except: pass
        return False


    def withdraw(customer_name, cash) -> bool:
        '''
    Withdraw command to update CASH at customer_id.\n
    Cash -= cash_input for user.\n
    takes 0 args, only asks inside of function.
    '''
        cursor = db.cursor()
        try:
            if int(cash) >= 0 and securityCheck(customer_name)==False:
                cursor.execute(f"update customers_table set customer_cash = customer_cash - {cash} where customer_name = '{customer_name}';")
                cursor.close()
                db.commit()
                return True
        except: pass
        return False


    def send(customer_name, cash, taker) -> bool:
        '''
    Send command to update CASH at customer_id[i] and customer_id[j].\n
    Sends cash from one user to another.\n
    takes 0 args, only asks inside of function.
    '''
        cursor = db.cursor()

        try: #check how much money customer do have
            print("Checking cash")
            cursor.execute(f"select customer_cash from customers_table where customer_name = '{customer_name}';")
            cash_on_sender_card = cursor.fetchone()[0]
            print(cash_on_sender_card)
        except: return False


        try:
            cash = int(cash)
            cash_on_sender_card = int(cash_on_sender_card)

            if cash >= 0 and cash_on_sender_card - cash >= 0 and securityCheck(customer_name, taker)==False:
                print("Sending cash")
                cursor.execute(f"update customers_table set customer_cash = customer_cash + {cash} where customer_name = '{taker}';")
                print("send #1")
                cursor.execute(f"update customers_table set customer_cash = customer_cash - {cash} where customer_name = '{customer_name}';")
                print("send #2")
                cursor.close()
                db.commit()
                return True
        except: pass
        return False
    

    def getCashAmount(customer_name):
        cursor = db.cursor()
        redis_client = redis.Redis("localhost", 6379)

        moneyFromcache = redis_client.get(customer_name)

        if moneyFromcache is None:
            print("set into cache")
            cursor.execute(f"select customer_cash from customers_table where customer_name = '{customer_name}';")
            customer_cash = cursor.fetchone()
            redis_client.set(customer_name, customer_cash[0])

        elif moneyFromcache is not None:
            print("from cache", moneyFromcache)
            return int(moneyFromcache)

        try:
            print("get from db")
            cursor.execute(f"select customer_cash from customers_table where customer_name = '{customer_name}';")
            customer_cash = cursor.fetchone()
            cursor.close()
            return customer_cash[0]
        except: pass




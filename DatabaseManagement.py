import os
import sqlite3


class DatabaseManagement:
    orderQueue = 'orderQueue.db'
    requestQueue = 'requestQueue.db'
    folder_path = 'database'

    # For debugging
    def checkDatabase(databaseName):
        os.makedirs(DatabaseManagement.folder_path, exist_ok=True)
        db_path = os.path.join(DatabaseManagement.folder_path, databaseName)
        con = sqlite3.connect(db_path)
        cur = con.cursor()
        cur.execute('''CREATE TABLE IF NOT EXISTS cocktailsOrder (orderNb INTEGER, userID INTEGER, cocktail TEXT) ''')
        member_data = cur.execute("SELECT * FROM cocktailsOrder ORDER BY orderNb")
        for row in member_data:
            print(row)
        cur.close()
        con.close()

    # After a cocktail is fetched from the request queue, add the next on in line from the ordering queue
    # If there is none, it is okay as the next placed order will be directly added to the request queue
    @staticmethod
    def databaseBalanceManagement():
        requestQueueNum = DatabaseManagement.checkNumQueue(DatabaseManagement.requestQueue)
        orderQueueNum = DatabaseManagement.checkNumQueue(DatabaseManagement.orderQueue)
        print(f"RequestQ {requestQueueNum} ----- OrderQ {orderQueueNum}")
        if requestQueueNum == 0 and orderQueueNum > 0:
            orderNb, user_id, cocktail = DatabaseManagement.dequeue(DatabaseManagement.orderQueue)
            DatabaseManagement.enqueue(DatabaseManagement.requestQueue, orderNb, user_id, cocktail)
            print("Moved an order to request Queue")

    # Function to fetch the maximum order number from the cocktail database
    @staticmethod
    def get_max_order_number(databaseName):
        os.makedirs(DatabaseManagement.folder_path, exist_ok=True)
        db_path = os.path.join(DatabaseManagement.folder_path, databaseName)
        con = sqlite3.connect(db_path)
        cursor = con.cursor()
        cursor.execute("SELECT MAX(orderNb) FROM cocktailsOrder")
        max_order_number = cursor.fetchone()[0]
        cursor.close()
        con.close()
        return max_order_number if max_order_number is not None else 0  # Return 0 if no entries are present

    @staticmethod
    def checkNumQueue(databaseName):
        os.makedirs(DatabaseManagement.folder_path, exist_ok=True)
        db_path = os.path.join(DatabaseManagement.folder_path, databaseName)
        con = sqlite3.connect(db_path)
        cur = con.cursor()
        cur.execute('''CREATE TABLE IF NOT EXISTS cocktailsOrder (orderNb INTEGER, userID INTEGER, cocktail TEXT) ''')
        cur.execute('''SELECT COUNT(*) AS entry_count FROM cocktailsOrder''')
        result = cur.fetchone()
        if result[0] > 0:
            # print(result[0])
            cur.close()
            con.close()
            return result[0]
        else:
            # print(result[0])
            cur.close()
            con.close()
            return 0

    # orderNb: -1 if it is a new order which needs a new number else its the old order number
    @staticmethod
    def enqueue(databaseName, orderNb, userID, cocktail):

        # Important because the order of the ordered cocktails is needed (FIFO)
        # The order number is only important in relation to each-other in the order queue
        if orderNb == -1:
            orderNb = DatabaseManagement.get_max_order_number(databaseName) + 1
        os.makedirs(DatabaseManagement.folder_path, exist_ok=True)
        db_path = os.path.join(DatabaseManagement.folder_path, databaseName)
        con = sqlite3.connect(db_path)
        cur = con.cursor()
        cur.execute('''CREATE TABLE IF NOT EXISTS cocktailsOrder (orderNb INTEGER, userID INTEGER, cocktail TEXT) ''')
        cur.execute('''INSERT INTO cocktailsOrder (orderNb, userID, cocktail) VALUES (?, ?, ?) ''',
                    (orderNb, userID, cocktail))
        con.commit()
        print(f"Enqueued:Order Number - {orderNb}, User ID - {userID} , Cocktail - {cocktail}")
        cur.close()
        con.close()

    @staticmethod
    def dequeue(databaseName):
        os.makedirs(DatabaseManagement.folder_path, exist_ok=True)
        db_path = os.path.join(DatabaseManagement.folder_path, databaseName)
        con = sqlite3.connect(db_path)
        cur = con.cursor()
        cur.execute('''SELECT orderNb, userID, cocktail FROM cocktailsOrder ORDER BY orderNb ASC LIMIT 1 ''')
        item = cur.fetchone()
        if item:
            cur.execute('''DELETE FROM cocktailsOrder WHERE orderNb=?''', (item[0],))
            con.commit()
            print(f"Dequeued: Order Number - {item[0]} , User ID - {item[1]}, Cocktail - {item[2]} ")
            cur.close()
            con.close()
            return item[0], item[1], item[2]  # Returning cocktail and userID
        else:
            # print("Queue is empty")
            cur.close()
            con.close()
            return None, None, None


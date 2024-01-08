import asyncio
import sqlite3
class DatabaseManagement:
    orderQueue = 'orderQueue.db'
    requestQueue = 'requestQueue.db'

    #TODO Reihenfolge in der Datenbank ist falsch. Brauche eine eigene Nummerierung. Order number einführen


    # For debugging
    def checkDatabase(databaseName):
        con = sqlite3.connect(databaseName)
        cur = con.cursor()
        cur.execute('''CREATE TABLE IF NOT EXISTS cocktail (orderNb INTEGER, userID INTEGER, cocktailName TEXT) ''')
        member_data = cur.execute("SELECT * FROM cocktail ORDER BY orderNb")
        for row in member_data:
            print(row)
        cur.close()
        con.close()



    async def databaseBalanceManagement(self):
        while True:
            requestQueueNum = self.checkNumQueue(self.requestQueue)
            orderQueueNum = self.checkNumQueue(self.orderQueue)

            if requestQueueNum == 0 & orderQueueNum > 0:
                cocktail_name, user_id = self.dequeue(self.orderQueue)
                self.enqueue(self.requestQueue, cocktail_name, user_id)
            await asyncio.sleep(2)  # Check request queue every 5 seconds

    # Function to fetch the maximum order number from the cocktail database
    @staticmethod
    def get_max_order_number(databaseName):
        conn = sqlite3.connect(databaseName)
        cursor = conn.cursor()
        cursor.execute("SELECT MAX(orderNb) FROM cocktail")
        max_order_number = cursor.fetchone()[0]
        cursor.close()
        conn.close()
        return max_order_number if max_order_number is not None else 0  # Return 0 if no entries are present

    @staticmethod
    def checkNumQueue(databaseName):
        con = sqlite3.connect(databaseName)
        cur = con.cursor()
        cur.execute('''CREATE TABLE IF NOT EXISTS cocktail (orderNb INTEGER, userID INTEGER, cocktailName TEXT) ''')
        cur.execute("SELECT COUNT(*) AS entry_count FROM cocktail")
        result = cur.fetchone()
        if result[0] > 0:
            print(result[0])
            cur.close()
            con.close()
            return result[0]
        else:
            print(result[0])
            cur.close()
            con.close()
            return 0

    @staticmethod
    def enqueue(databaseName, cocktail_name, user_id):
        orderNb = DatabaseManagement.get_max_order_number(databaseName) + 1
        con = sqlite3.connect(databaseName)
        cur = con.cursor()
        cur.execute('''CREATE TABLE IF NOT EXISTS cocktail (orderNb INTEGER, userID INTEGER, cocktailName TEXT) ''')
        cur.execute('''INSERT INTO cocktail (orderNb, userID, cocktailName) VALUES (?, ?, ?) ''', (orderNb, cocktail_name, user_id))
        con.commit()
        print(f"Enqueued:Order Number - {orderNb}, User ID - {user_id} , Cocktail Name - {cocktail_name}")
        cur.close()
        con.close()

    #TODo check if item array is right starting from 0 or 1 (depending on the data structure)
    @staticmethod
    def dequeue(databaseName):
        con = sqlite3.connect(databaseName)
        cur = con.cursor()
        cur.execute('''SELECT orderNb, userID, cocktailName FROM cocktail ORDER BY orderNb DESC LIMIT 1 ''')
        item = cur.fetchone()
        if item:
            cur.execute('''DELETE FROM cocktail WHERE orderNb=?''', (item[1]))
            con.commit()
            print(f"Dequeued: Order Number - {item[0]} , User ID - {item[1]}, Cocktail Name - {item[2]} ")
            cur.close()
            con.close()
            return item[0], item[1], item[2]  # Returning cocktailName and userID
        else:
            print("Queue is empty")
            cur.close()
            con.close()
            return None, None
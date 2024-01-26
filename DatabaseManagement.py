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
        cur.execute('''CREATE TABLE IF NOT EXISTS items (orderNb INTEGER, expr TEXT, item TEXT, userID INTEGER, timestamp TEXT) ''')
        member_data = cur.execute("SELECT * FROM items ORDER BY orderNb")
        for row in member_data:
            print(row)
        cur.close()
        con.close()

    # After a cocktail is fetched from the request queue, add the next on in line from the ordering queue
    # If there is none, it is okay as the next placed order will be directly added to the request queue
    # @staticmethod
    # def databaseBalanceManagement():
    #     requestQueueNum = DatabaseManagement.checkNumQueue(DatabaseManagement.requestQueue)
    #     orderQueueNum = DatabaseManagement.checkNumQueue(DatabaseManagement.orderQueue)
    #     print(f"RequestQ {requestQueueNum} ----- OrderQ {orderQueueNum}")
    #     if requestQueueNum == 0 and orderQueueNum > 0:
    #         orderNb, user_id, cocktail = DatabaseManagement.dequeue(DatabaseManagement.orderQueue)
    #         DatabaseManagement.enqueue(DatabaseManagement.requestQueue, orderNb, user_id, cocktail)
    #         print("Moved an order to request Queue")

    # Function to fetch the maximum order number from the current cocktail database

    @staticmethod
    def process_data(databaseName, data, callback_url):
        os.makedirs(DatabaseManagement.folder_path, exist_ok=True)
        db_path = os.path.join(DatabaseManagement.folder_path, databaseName)
        con = sqlite3.connect(db_path)
        cur = con.cursor()

        # Create the 'items' table if it doesn't exist (assuming you haven't done it already)
        cur.execute(
            '''CREATE TABLE IF NOT EXISTS items (orderNb INTEGER, expr TEXT, item TEXT, userID INTEGER, timestamp TEXT)''')

        # Build the base query
        query = '''
            SELECT *
            FROM items
            WHERE expr = ?
        '''

        # Add conditions for 'from' and 'to' if they exist in the data
        if 'item' in data:
            query += ' AND item = ?'
        if 'from' in data:
            query += ' AND timestamp >= ?'
        if 'to' in data:
            query += ' AND timestamp <= ?'

        # Add conditions for 'banned_users' if it exists in the data
        if 'banned_users' in data and data['banned_users']:
            query += ' AND userID NOT IN ({})'.format(', '.join(['?' for _ in data['banned_users']]))

        # Execute the query with parameters
        params = [data['expr']]
        if 'item' in data:
            params.append((data['item']))
        if 'from' in data:
            params.append(data['from'])
        if 'to' in data:
            params.append(data['to'])
        if 'banned_users' in data and data['banned_users']:
            params.extend(data['banned_users'])

        cur.execute(query, params)

        # Fetch the result
        #result = cur.fetchone()
        all_results = cur.fetchall()
        print(all_results)
        #print(result)
        # # Check if a matching entry was found
        # if result:
        #     print("Matching entry found.")
        # else:
        #     print("No matching entry found.")

        # Close the connection
        con.close()


        return None

    @staticmethod
    def checkBannedUsers(databaseName, banned_users):

        os.makedirs(DatabaseManagement.folder_path, exist_ok=True)
        db_path = os.path.join(DatabaseManagement.folder_path, databaseName)
        con = sqlite3.connect(db_path)
        cursor = con.cursor()
        query = f"SELECT * FROM items WHERE userID NOT IN ({', '.join(['?' for _ in banned_users])});"
        cursor.execute(query, banned_users)
        results = cursor.fetchall()
        print(results)

        con.close()


    @staticmethod
    def get_max_order_number(databaseName):
        os.makedirs(DatabaseManagement.folder_path, exist_ok=True)
        db_path = os.path.join(DatabaseManagement.folder_path, databaseName)
        con = sqlite3.connect(db_path)
        cursor = con.cursor()
        cursor.execute("SELECT MAX(orderNb) FROM items")
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
        cur.execute('''CREATE TABLE IF NOT EXISTS items (orderNb INTEGER, expr TEXT, item TEXT, userID INTEGER, timestamp TEXT) ''')
        cur.execute('''SELECT COUNT(*) AS entry_count FROM items''')
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
    def enqueue(databaseName, orderNb, expr, item, userID, timestamp):

        # Important because the order of the ordered cocktails is needed (FIFO)
        # The order number is only important in relation to each-other in the order queue
        if orderNb == -1:
            orderNb = DatabaseManagement.get_max_order_number(databaseName) + 1
        os.makedirs(DatabaseManagement.folder_path, exist_ok=True)
        db_path = os.path.join(DatabaseManagement.folder_path, databaseName)
        con = sqlite3.connect(db_path)
        cur = con.cursor()
        cur.execute('''CREATE TABLE IF NOT EXISTS items (orderNb INTEGER, expr TEXT, item TEXT, userID INTEGER, timestamp TEXT) ''')
        #cur.execute('''INSERT INTO items (orderNb INTEGER, expr TEXT, item TEXT, userID INTEGER, timestamp TEXT) VALUES (?, ?, ?, ?, ?) ''',
        #            (orderNb, expr, item, userID, timestamp))
        cur.execute('''INSERT INTO items (orderNb, expr, item, userID, timestamp) VALUES (?, ?, ?, ?, ?)''',
                    (orderNb, expr, item, userID, timestamp))

        con.commit()
        print(f"Enqueued: Order Number - {orderNb}, Expr {expr} , Item {item}, User ID - {userID} , Timestamp - {timestamp}")
        cur.close()
        con.close()

    @staticmethod
    def dequeue(databaseName, orderNb):
        os.makedirs(DatabaseManagement.folder_path, exist_ok=True)
        db_path = os.path.join(DatabaseManagement.folder_path, databaseName)
        con = sqlite3.connect(db_path)
        cur = con.cursor()
        cur.execute('''SELECT orderNb, expr, item, userID, timestamp FROM items WHERE orderNb=?''', (orderNb,))
        item = cur.fetchone()
        if item:
            cur.execute('''DELETE FROM items WHERE orderNb=?''', (item[0],))
            con.commit()
            print(f"Dequeued: Order Number - {item[0]}, Expr {item[1]} , Item {item[2]}, User ID - {item[3]} , Timestamp - {item[4]}")
            cur.close()
            con.close()
            return item[0], item[1], item[2], item[3], item[4]
        else:
            # print("Queue is empty")
            cur.close()
            con.close()
            return None, None, None, None, None

if __name__ == "__main__":
    #DatabaseManagement.enqueue("RequestQueue", 1,"order", "Negroni", 212,"12:30:12")
    #DatabaseManagement.enqueue("RequestQueue", 2,"order", "Margerita", 123,"15:30:12")
    #DatabaseManagement.enqueue("RequestQueue", 3,"order", "Old Fashioned", 456,"19:30:12")
    #DatabaseManagement.checkBannedUsers("RequestQueue", [212])
    data = {
        'expr': "order",
        'from': "11:00:00",
        'to': "20:00:00",
        'banned_users': [212]
    }
    DatabaseManagement.process_data("RequestQueue", data, "www.google.de")
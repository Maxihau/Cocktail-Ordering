import os
import sqlite3
import time as mytime
from datetime import datetime


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
        cur.execute(
            '''CREATE TABLE IF NOT EXISTS items (orderNb INTEGER, expr TEXT, item TEXT, userID INTEGER, timestamp TEXT) ''')
        member_data = cur.execute("SELECT * FROM items ORDER BY orderNb")
        for row in member_data:
            print(row)
        cur.close()
        con.close()



    @staticmethod
    def createFilter(filterCriteria, databaseName):
        os.makedirs(DatabaseManagement.folder_path, exist_ok=True)
        db_path = os.path.join(DatabaseManagement.folder_path, databaseName)
        con = sqlite3.connect(db_path)
        cur = con.cursor()

        cur.execute(
            '''CREATE TABLE IF NOT EXISTS filters (expr TEXT, item TEXT, from_time TEXT, to_time TEXT, banned_users TEXT, callbackURL TEXT, timestamp TEXT)''')

        insert_query = '''
                INSERT INTO filters (expr, item, from_time, to_time, banned_users, callbackURL)
                VALUES (?, ?, ?, ?, ?, ?)
            '''

        if filterCriteria['banned_users'] is None:
            banned_users_str = None
        else:
            banned_users_str = ','.join(filterCriteria['banned_users'])

        # Execute the query and commit the changes
        cur.execute(insert_query, (
            filterCriteria['expr'], filterCriteria['item'], filterCriteria['from'], filterCriteria['to'],
            banned_users_str, filterCriteria['callbackURL']))
        con.commit()
        con.close()

    @staticmethod
    def convert_filter_to_data(row):

        banned_users_str = row[4]

        if banned_users_str is None:
            banned_users = None
        else:
            banned_users = banned_users_str.split(',')

        data_object = {
            'expr': row[0],
            'item': row[1],
            'from': row[2],
            'to': row[3],
            'banned_users': banned_users,  # Assuming banned_users is a comma-separated string
            'callbackURL': row[5]
        }

        return data_object



    @staticmethod
    def getAllFilters():
        os.makedirs(DatabaseManagement.folder_path, exist_ok=True)
        db_path = os.path.join(DatabaseManagement.folder_path, DatabaseManagement.requestQueue)
        con = sqlite3.connect(db_path)
        cur = con.cursor()
        cur.execute(
            '''CREATE TABLE IF NOT EXISTS filters (expr TEXT, item TEXT, from_time TEXT, to_time TEXT, banned_users TEXT, callbackURL TEXT, timestamp TEXT)''')

        # Define the SQL query to select all data from your table
        select_all_query = '''
            SELECT * FROM filters
        '''

        # Execute the query
        cur.execute(select_all_query)

        # Fetch all the results
        results = cur.fetchall()

        # Close the connection
        con.close()

        return results

    @staticmethod
    def process_data(databaseName, filterCriteria):
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
        if 'item' in filterCriteria and filterCriteria['item'] is not None:
            query += ' AND item = ?'
        if 'from' in filterCriteria and filterCriteria['from'] is not None:
            query += ' AND timestamp >= ?'
        if 'to' in filterCriteria and filterCriteria['to'] is not None:
            query += ' AND timestamp <= ?'

        # Add conditions for 'banned_users' if it exists in the data
        if 'banned_users' in filterCriteria and filterCriteria['banned_users'] is not None and filterCriteria['banned_users']:
            query += ' AND userID NOT IN ({})'.format(', '.join(['?' for _ in filterCriteria['banned_users']]))

        query += 'ORDER BY orderNb ASC'

        # Execute the query with parameters
        params = [filterCriteria['expr']]
        if 'item' in filterCriteria and filterCriteria['item'] is not None:
            params.append((filterCriteria['item']))
        if 'from' in filterCriteria and filterCriteria['from'] is not None:
            params.append(filterCriteria['from'])
        if 'to' in filterCriteria and filterCriteria['to'] is not None:
            params.append(filterCriteria['to'])
        if 'banned_users' in filterCriteria and filterCriteria['banned_users'] is not None and filterCriteria['banned_users']:
            params.extend(filterCriteria['banned_users'])

        cur.execute(query, params)

        # Fetch the result
        result = cur.fetchone()

        # all_results = cur.fetchall()
        # print(all_results)
        # print(result)
        # Check if a matching entry was found
        if result:
            print("Matching entry found.")
        else:
            print("No matching entry found.")

        # Close the connection
        cur.close()
        con.close()
        if result:
            print(f"Result found: {result}")
            return DatabaseManagement.wrapToData(result)

        return None

    @staticmethod
    def wrapToData(result):
        data = {
            'orderNb': result[0],
            'expr': result[1],
            'item': result[2],
            'userID': result[3],
            'timestamp': result[4]
        }
        return data
    @staticmethod
    def deleteFilterByCallbackURL(callback_url):
        os.makedirs(DatabaseManagement.folder_path, exist_ok=True)
        db_path = os.path.join(DatabaseManagement.folder_path, DatabaseManagement.requestQueue)
        con = sqlite3.connect(db_path)
        cur = con.cursor()
        delete_query = '''
            DELETE FROM filters
            WHERE callbackURL = ?
        '''
        cur.execute(delete_query, (callback_url,))
        con.commit()
        con.close()

    @staticmethod
    def matchFilterData(filter_criteria, data):
        # Handle None values for filter_criteria['from'] and filter_criteria['to']
        from_time_str = filter_criteria['from']
        to_time_str = filter_criteria['to']

        if from_time_str is not None:
            from_time = datetime.strptime(from_time_str, '%H:%M').time()
        else:
            from_time = None

        if to_time_str is not None:
            to_time = datetime.strptime(to_time_str, '%H:%M').time()
        else:
            to_time = None

        # Convert timestamp to datetime object, handle None value for data['timestamp']
        timestamp_str = data['timestamp']
        if timestamp_str is not None:
            data_time = datetime.strptime(timestamp_str, '%H:%M:%S').time()
        else:
            # Handle the case where timestamp is None
            data_time = None

        # Check if the filter criteria is true or false
        filter_result = (
                (filter_criteria['expr'] is None or data['expr'] == filter_criteria['expr']) and
                (filter_criteria['item'] is None or data['item'] == filter_criteria['item']) and
                (from_time is None or (data_time is not None and from_time <= data_time)) and
                (to_time is None or (data_time is not None and data_time <= to_time)) and
                (filter_criteria['banned_users'] is None or data['userID'] not in filter_criteria['banned_users'])
            # Add more conditions as needed
        )
        return filter_result

    @staticmethod
    def checkDatabaseEntry(databaseName):
        os.makedirs(DatabaseManagement.folder_path, exist_ok=True)
        db_path = os.path.join(DatabaseManagement.folder_path, databaseName)
        con = sqlite3.connect(db_path)
        cursor = con.cursor()

        while True:
            # Execute a SELECT query to check for the desired entry
            query = f"SELECT * FROM items"
            cursor.execute(query)
            result = cursor.fetchone()

            if result:
                DatabaseManagement.dequeue(DatabaseManagement.requestQueue, result[0])
                print("Result found!")
                # Entry found, close the connection and return the result
                con.close()
                return result

            # Entry not found, wait for a while and then check again
            mytime.sleep(1)

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
        cur.execute(
            '''CREATE TABLE IF NOT EXISTS items (orderNb INTEGER, expr TEXT, item TEXT, userID INTEGER, timestamp TEXT) ''')
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
        cur.execute(
            '''CREATE TABLE IF NOT EXISTS items (orderNb INTEGER, expr TEXT, item TEXT, userID INTEGER, timestamp TEXT) ''')
        # cur.execute('''INSERT INTO items (orderNb INTEGER, expr TEXT, item TEXT, userID INTEGER, timestamp TEXT) VALUES (?, ?, ?, ?, ?) ''',
        #            (orderNb, expr, item, userID, timestamp))
        cur.execute('''INSERT INTO items (orderNb, expr, item, userID, timestamp) VALUES (?, ?, ?, ?, ?)''',
                    (orderNb, expr, item, userID, timestamp))

        con.commit()
        print(
            f"Enqueued in Database: {databaseName}: Order Number - {orderNb}, Expr {expr} , Item {item}, User ID - {userID} , Timestamp - {timestamp}")
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
            print(
                f"Dequeued in Database: {databaseName}: Order Number - {item[0]}, Expr {item[1]} , Item {item[2]}, User ID - {item[3]} , Timestamp - {item[4]}")
            cur.close()
            con.close()
            return item[0], item[1], item[2], item[3], item[4]
        else:
            # print("Queue is empty")
            cur.close()
            con.close()
            return None, None, None, None, None


if __name__ == "__main__":
    # DatabaseManagement.enqueue("orderQueue", 1,"order", "Negroni", 212,"12:30:12")
    # DatabaseManagement.enqueue("orderQueue", 2,"order", "Margerita", 123,"15:30:12")
    # DatabaseManagement.enqueue("RequestQueue", 3,"order", "Old Fashioned", 456,"19:30:12")
    # DatabaseManagement.checkBannedUsers("RequestQueue", [212])
    data = {
        'expr': "order",
        'from': None,
        'to': None,
        'banned_users': [212]
    }
    DatabaseManagement.process_data("orderQueue", data)

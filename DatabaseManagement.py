import os
import sqlite3
from datetime import datetime


class DatabaseManagement:
    order_queue = 'orderQueue.db'
    request_queue = 'requestQueue.db'
    folder_path = 'database'

    # For debugging
    # def check_database(databaseName):
    #     os.makedirs(DatabaseManagement.folder_path, exist_ok=True)
    #     db_path = os.path.join(DatabaseManagement.folder_path, databaseName)
    #     con = sqlite3.connect(db_path)
    #     cur = con.cursor()
    #     cur.execute(
    #         '''CREATE TABLE IF NOT EXISTS items (orderNb INTEGER, expr TEXT, item TEXT, userID INTEGER, timestamp TEXT) ''')
    #     member_data = cur.execute("SELECT * FROM items ORDER BY orderNb")
    #     for row in member_data:
    #         print(row)
    #     cur.close()
    #     con.close()

    @staticmethod
    def enqueue_filter(filterCriteria, databaseName):
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

        if filterCriteria['item'] is not None:
            items_list = filterCriteria['item']
            filterCriteria['item'] = ','.join(map(str, items_list))

        if filterCriteria['banned_users'] is None:
            banned_users_str = None
        elif len(filterCriteria['banned_users']) == 0:
            banned_users_str = None
        else:
            banned_users_str = ','.join(map(str, filterCriteria['banned_users']))

        # Execute the query and commit the changes
        cur.execute(insert_query, (
            filterCriteria['expr'], filterCriteria['item'], filterCriteria['from'], filterCriteria['to'],
            banned_users_str, filterCriteria['callbackURL']))
        con.commit()
        con.close()

    # Needed for the matching to match with the order request
    @staticmethod
    def convert_request_to_data(row):
        banned_users_str = row[4]
        if banned_users_str is None:
            banned_users = None
        else:
            banned_users = [int(user_id) for user_id in banned_users_str.split(',') if user_id.strip()]

        data_object = {
            'expr': row[0],
            'item': row[1],
            'from': row[2],
            'to': row[3],
            'banned_users': banned_users,
            'callbackURL': row[5]
        }

        return data_object

    @staticmethod
    def get_all_requests():
        os.makedirs(DatabaseManagement.folder_path, exist_ok=True)
        db_path = os.path.join(DatabaseManagement.folder_path, DatabaseManagement.request_queue)
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

    # Processes the new filter/ service from the CPEE by checking if it matches the already existing orders in the queue
    @staticmethod
    def match_new_request(databaseName, filterCriteria):
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
        # Modify the 'item' condition to use the IN operator if multiple items are provided
        if 'item' in filterCriteria and filterCriteria['item'] is not None:
            items_list = filterCriteria['item']
            query += f' AND item IN ({", ".join(["?" for _ in items_list])})'
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
            params.extend(items_list)
        if 'from' in filterCriteria and filterCriteria['from'] is not None:
            params.append(filterCriteria['from'])
        if 'to' in filterCriteria and filterCriteria['to'] is not None:
            params.append(filterCriteria['to'])
        if 'banned_users' in filterCriteria and filterCriteria['banned_users'] is not None and filterCriteria['banned_users']:
            params.extend(filterCriteria['banned_users'])

        cur.execute(query, params)

        # Fetch the result
        result = cur.fetchone()

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
            return DatabaseManagement.wrap_to_data(result)

        return None

    @staticmethod
    def wrap_to_data(result):
        data = {
            'orderNb': result[0],
            'expr': result[1],
            'item': result[2],
            'userID': result[3],
            'timestamp': result[4]
        }
        return data

    @staticmethod
    def dequeue_filter_by_callback_url(callback_url):
        os.makedirs(DatabaseManagement.folder_path, exist_ok=True)
        db_path = os.path.join(DatabaseManagement.folder_path, DatabaseManagement.request_queue)
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
    def match_new_order(filter_criteria, data, item):
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

        item_matches = (
                item in filter_criteria['item']
        )

        # Check if the filter criteria is true or false
        filter_result = (
                (filter_criteria['expr'] is None or data['expr'] == filter_criteria['expr']) and
                item_matches and
                (from_time is None or (data_time is not None and from_time <= data_time)) and
                (to_time is None or (data_time is not None and data_time <= to_time)) and
                (filter_criteria['banned_users'] is None or data['userID'] not in filter_criteria['banned_users'])
            # Add more conditions as needed
        )
        return filter_result

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
    def enqueue_order(databaseName, orderNb, expr, item, userID, timestamp):

        # Important because the order of the ordered cocktails is needed (FIFO)
        # The order number is only important in relation to each-other in the order queue
        # orderNb: -1 if it is a new order which needs a new number else its the old order number
        if orderNb == -1:
            orderNb = DatabaseManagement.get_max_order_number(databaseName) + 1
        os.makedirs(DatabaseManagement.folder_path, exist_ok=True)
        db_path = os.path.join(DatabaseManagement.folder_path, databaseName)
        con = sqlite3.connect(db_path)
        cur = con.cursor()
        cur.execute(
            '''CREATE TABLE IF NOT EXISTS items (orderNb INTEGER, expr TEXT, item TEXT, userID INTEGER, timestamp TEXT) ''')
        cur.execute('''INSERT INTO items (orderNb, expr, item, userID, timestamp) VALUES (?, ?, ?, ?, ?)''',
                    (orderNb, expr, item, userID, timestamp))

        con.commit()
        print(
            f"Enqueued in Database: {databaseName}: Order Number - {orderNb}, Expr {expr} , Item {item}, User ID - {userID} , Timestamp - {timestamp}")
        cur.close()
        con.close()

    @staticmethod
    def dequeue_order(databaseName, orderNb):
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
            cur.close()
            con.close()
            return None, None, None, None, None


class WordsRepository:

    @staticmethod
    def add_word_to_wordsDB(word):
        os.makedirs(DatabaseManagement.folder_path, exist_ok=True)
        db_path = os.path.join(DatabaseManagement.folder_path, "words.db")
        con = sqlite3.connect(db_path)
        cur = con.cursor()
        try:
            # Check if the item already exists in the database
            if word not in WordsRepository.get_all_valid_words():
                # Execute a query to insert the item into the database
                cur.execute(
                    '''CREATE TABLE IF NOT EXISTS words (name TEXT) ''')
                cur.execute("INSERT INTO words (name) VALUES (?)", (word,))

                # Commit the changes to the database
                con.commit()
                print(f"Item '{word}' added to the database.")
            else:
                print(f"Item '{word}' already exists in the database and will not be added.")
        finally:
            # Close the database connection
            con.close()

    # Extracts all words from the database to be checked if the target word contains a type
    @staticmethod
    def get_all_valid_words():
        os.makedirs(DatabaseManagement.folder_path, exist_ok=True)
        db_path = os.path.join(DatabaseManagement.folder_path, "words.db")
        con = sqlite3.connect(db_path)
        cur = con.cursor()

        try:
            cur.execute(
                '''CREATE TABLE IF NOT EXISTS words (name TEXT) ''')
            # Execute a query to fetch all valid items
            cur.execute("SELECT name FROM words")

            # Fetch all the rows as a list of tuples
            rows = cur.fetchall()

            # Extract the item names from the tuples
            valid_words = [row[0] for row in rows]

            return valid_words

        finally:
            # Close the database connection
            con.close()

#For test purposes
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
    DatabaseManagement.match_new_request("orderQueue", data)

from bottle import get, post, request, Bottle, abort

import sqlite3

from NumberTooBigError import NumberTooBigError

app = Bottle()
orderQueue = 'orderQueue.db'
requestQueue = 'requestQueue.db'

#For debugging
def checkDatabase(databaseName):
    con = sqlite3.connect(databaseName)
    cur = con.cursor()
    member_data = cur.execute("SELECT * FROM cocktail ORDER BY userID")
    for row in member_data:
        print(row)
    cur.close()
    con.close()

def checkNumQueue(databaseName):
    con = sqlite3.connect(databaseName)
    cur = con.cursor()
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

def enqueue(databaseName, cocktail_name, user_id):
    con = sqlite3.connect(databaseName)
    cur = con.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS cocktail (cocktailName TEXT, userID INTEGER) ''')
    cur.execute('''INSERT INTO cocktail (cocktailName, userID) VALUES (?, ?) ''', (cocktail_name, user_id))
    con.commit()
    print(f"Enqueued: Cocktail Name - {cocktail_name}, User ID - {user_id}")
    cur.close()
    con.close()

def dequeue(databaseName):
    con = sqlite3.connect(databaseName)
    cur = con.cursor()
    cur.execute('''SELECT id, cocktailName, userID FROM cocktail ORDER BY id LIMIT 1 ''')
    item = cur.fetchone()
    if item:
        cur.execute('''DELETE FROM cocktail WHERE id=?''', (item[0],))
        con.commit()
        print(f"Dequeued: Cocktail Name - {item[1]}, User ID - {item[2]}")
        enqueue(requestQueue,item[1], item[2])
        cur.close()
        con.close()
        return item[1], item[2]  # Returning cocktailName and userID
    else:
        print("Queue is empty")
        cur.close()
        con.close()
        return None, None

# Add the order to the right queue (or database)
def addOrdering(cocktail_name, user_id):
    numQueueRequest = checkNumQueue(requestQueue)
    numQueueOrder = checkNumQueue(orderQueue)
    if numQueueRequest == 0 & numQueueOrder >= 0:
        enqueue(requestQueue, cocktail_name, user_id)
    elif numQueueRequest == 1 & numQueueOrder >= 0:
        enqueue(orderQueue, cocktail_name, user_id)
    else:
        raise NumberTooBigError()

@app.route('/', method='POST')
def order_cocktail():
    data = request.json  # Get JSON data from the POST request

    if 'cocktailName' in data and 'userID' in data:
        cocktail_name = data['cocktailName']
        user_id = data['userID']
        print(cocktail_name)
        print(user_id)

        try:
            addOrdering(cocktail_name,user_id)
        except NumberTooBigError as e:
            print(e)
            abort(500, "There was an internal error.")
        except Exception as e:
            print(e)
            abort(500, "Unknown error. Check server console")
        # Print the cocktail and the customer's name
        print(f"New Order: {cocktail_name} ordered by {user_id}")
        return ''

    else:
        abort(422, "Wrong data (format)")


if __name__ == "__main__":

    #enqueue(orderQueue,"negroni",21312)
    #checkQueue(orderQueue)
    #checkDatabase()
    #checkQueue(orderQueue)
    app.run(host='localhost', port=8080, debug=True)
    #app.run(host="::", port=5123)  # Runs the application on port 5000

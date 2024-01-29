import requests
from bottle import request, Bottle, abort
from DatabaseManagement import DatabaseManagement
from NumberTooBigError import NumberTooBigError

app = Bottle()
# Access to both databases
orderQueue = 'orderQueue.db'
requestQueue = 'requestQueue.db'


# Used when an HTTP is posted here
# Adds the order to the right queue (or database)
def add_item(expr, item, userID, timestamp):
    # Check the number of both databases
    numQueueRequest = DatabaseManagement.checkNumQueue(requestQueue)
    numQueueOrder = DatabaseManagement.checkNumQueue(orderQueue)

    # Checks if a cocktail is already in the request queue
    # If not, add it to the request queue
    # If yes, then add it to the order queue
    try:
        DatabaseManagement.enqueue(orderQueue, -1, expr, item, userID, timestamp)
    except Exception as e:
        print(f"Error while trying to a an item: {e}")
        raise e


def matching(data):
    filters = DatabaseManagement.getAllFilters()

    for filter in filters:
        print("Checking filter")
        processedFilter = DatabaseManagement.convert_filter_to_data(filter)
        result = DatabaseManagement.matchFilterData(processedFilter, data)
        if result:
            print("Result found in matching")
            DatabaseManagement.deleteFilterByCallbackURL(filter[5])
            callback(data, filter[5])
            print(processedFilter)
            return True
    return False


def callback(result, callbackURL):
    # headers = {'Content-Type': 'application/json'}
    response = requests.put(callbackURL, json=result)
    print(f"Response of Callback: {response}")


# Handles the POST Request
@app.route('/', method='POST')
def expr_item():
    data = request.json

    if 'expr' in data and 'item' in data and 'userID' in data and 'timestamp' in data:
        expr = data['expr']
        item = data['item']
        userID = data['userID']
        timestamp = data['timestamp']

        print(expr)
        print(item)
        print(userID)
        print(timestamp)

        try:
            if not matching(data):
                print("Added item to OrderQueue")
                add_item(expr, item, userID, timestamp)
        except NumberTooBigError as e:
            print(e)
            abort(500, "There was an internal error with the database. Please check console")
        except Exception as e:
            print(e)
            abort(500, "Unknown error. Check server console")

        # Print the cocktail and the customer's name
        print(f"Expr {expr} with Item: {item} requested by {userID} at time: {timestamp}")
        return ''
    else:
        abort(422, "Wrong data (format)")


if __name__ == "__main__":
    # Local testing
    app.run(host='localhost', port=8080, debug=True)
    #app.run(host="::", port=5321)

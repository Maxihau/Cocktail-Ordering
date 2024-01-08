from bottle import request, Bottle, abort

from DatabaseManagement import DatabaseManagement
from NumberTooBigError import NumberTooBigError

app = Bottle()
orderQueue = 'orderQueue.db'
requestQueue = 'requestQueue.db'

# Add the order to the right queue (or database)
def addOrdering(userID,cocktail_name):
    numQueueRequest = DatabaseManagement.checkNumQueue(requestQueue)
    numQueueOrder = DatabaseManagement.checkNumQueue(orderQueue)
    if numQueueRequest == 0 and numQueueOrder >= 0:
        DatabaseManagement.enqueue(requestQueue, -1, userID, cocktail_name)
    elif numQueueRequest == 1 and numQueueOrder >= 0:
        DatabaseManagement.enqueue(orderQueue, -1, userID, cocktail_name)
    else:
        raise NumberTooBigError()


@app.route('/', method='POST')
def order_cocktail():
    data = request.json  # Get JSON data from the POST request

    if 'cocktailName' in data and 'userID' in data:
        cocktail_name = data['cocktailName']
        userID = data['userID']
        print(cocktail_name)
        print(userID)

        try:
            addOrdering(userID, cocktail_name)
        except NumberTooBigError as e:
            print(e)
            abort(500, "There was an internal error.")
        except Exception as e:
            print(e)
            abort(500, "Unknown error. Check server console")
        # Print the cocktail and the customer's name
        print(f"New Order: {cocktail_name} ordered by {userID}")
        return ''
    else:
        abort(422, "Wrong data (format)")


if __name__ == "__main__":
    #app.run(host='localhost', port=8080, debug=True)
    app.run(host="::", port=5321)  # Runs the application on port 5000


    #dbManagement = DatabaseManagement()
    #asyncio.run(dbManagement.databaseBalanceManagement())


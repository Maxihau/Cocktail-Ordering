from bottle import request, Bottle, abort
from DatabaseManagement import DatabaseManagement
from NumberTooBigError import NumberTooBigError

app = Bottle()
# Access to both databases
orderQueue = 'orderQueue.db'
requestQueue = 'requestQueue.db'


# Used when an HTTP is posted here
# Adds the order to the right queue (or database)
def addOrdering(userID, cocktail):
    # Check the number of both databases
    numQueueRequest = DatabaseManagement.checkNumQueue(requestQueue)
    numQueueOrder = DatabaseManagement.checkNumQueue(orderQueue)

    # Checks if a cocktail is already in the request queue
    # If not, add it to the request queue
    # If yes, then add it to the order queue
    if numQueueRequest == 0 and numQueueOrder >= 0:
        DatabaseManagement.enqueue(requestQueue, -1, userID, cocktail)
    elif numQueueRequest == 1 and numQueueOrder >= 0:
        DatabaseManagement.enqueue(orderQueue, -1, userID, cocktail)
    else:
        # Error, if request queue is not 0/1 or order queue is <0
        raise NumberTooBigError()


# Handles the POST Request
@app.route('/', method='POST')
def order_cocktail():
    data = request.json

    if 'cocktail' in data and 'userID' in data:
        cocktail = data['cocktail']
        userID = data['userID']
        print(cocktail)
        print(userID)

        try:
            addOrdering(userID, cocktail)
        except NumberTooBigError as e:
            print(e)
            abort(500, "There was an internal error with the database. Please check console")
        except Exception as e:
            print(e)
            abort(500, "Unknown error. Check server console")

        # Print the cocktail and the customer's name
        print(f"New Order: {cocktail} ordered by {userID}")
        return ''
    else:
        abort(422, "Wrong data (format)")


if __name__ == "__main__":
    # Local testing
    # app.run(host='localhost', port=8080, debug=True)

    app.run(host="::", port=5321)

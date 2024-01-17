from bottle import request, Bottle
from DatabaseManagement import DatabaseManagement

app = Bottle()

# Access to both databases
orderQueue = 'orderQueue.db'
requestQueue = 'requestQueue.db'


@app.route('/', method='POST')
def order():
    # Access the form data
    form_data = request.forms
    form_data_dict = dict(form_data)

    print(form_data_dict)

    data = {
        'orderNb': '',
        'user_id': '',
        'cocktail_name': ''
    }
    data_isEmpty = any(value == '' for value in data.values())

    # Checks in a loop if a cocktail has been ordered
    # Use case: Script still has to check for a cocktail in RequestQueue.db even no order is in both queues
    while data_isEmpty:
        orderNb, user_id, cocktail = DatabaseManagement.dequeue(requestQueue)

        # Checks if the dequeued data is no empty. If yes, add it to the data to send it back to CPEE via callback
        if cocktail is not None and user_id is not None and orderNb is not None:
            data['orderNb'] = orderNb
            data['user_id'] = user_id
            data['cocktail'] = cocktail
            data_isEmpty = False
            DatabaseManagement.databaseBalanceManagement()
            print(f"New Order: {cocktail} ordered by {user_id} with order number {orderNb}")

    return data


if __name__ == "__main__":
    app.run(host="::", port=5123)
    # app.run(host='localhost', port=8081, debug=True)

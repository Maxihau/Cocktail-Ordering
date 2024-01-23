from ast import literal_eval
import concurrent.futures
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

    callback_url = request.headers.get("CPEE-Callback")
    print(f"Callback URL: {callback_url}")

    print(form_data_dict)
    pattern = request.forms.get('pattern')
    print(f"Pattern: {pattern}")
    pattern_array = literal_eval(str(pattern))
    expr = pattern_array[0]
    item = pattern_array[1]

    # Optionally get 'from', 'to', and 'banned_users' fields
    form_from = request.forms.get('from')
    print(f"From: {form_from}")
    form_to = request.forms.get('to')
    print(f"To: {form_to}")

    # Convert 'banned_users' string to a list
    banned_users = request.forms.get('banned_users')
    banned_users_array = literal_eval(str(banned_users))
    print(f"Banned users: {banned_users}")

    data = {
        'expr': expr,
        'item': item,
        'from': form_from,
        'to': form_to,
        'banned_users': banned_users_array
    }

    # Use a thread pool to call the processing function asynchronously
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future = executor.submit(process_data, data, callback_url)


    # # Checks in a loop if a cocktail has been ordered
    # # Use case: Script still has to check for a cocktail in RequestQueue.db even no order is in both queues
    # while data_isEmpty:
    #     orderNb, user_id, cocktail = DatabaseManagement.dequeue(requestQueue)
    #
    #     # Checks if the dequeued data is no empty. If yes, add it to the data to send it back to CPEE via callback
    #     if cocktail is not None and user_id is not None and orderNb is not None:
    #         data['orderNb'] = orderNb
    #         data['user_id'] = user_id
    #         data['cocktail'] = cocktail
    #         data_isEmpty = False
    #         DatabaseManagement.databaseBalanceManagement()
    #         print(f"New Order: {cocktail} ordered by {user_id} with order number {orderNb}")

    return ''


if __name__ == "__main__":
    #app.run(host="::", port=5123)
    app.run(host='localhost', port=8081, debug=True)

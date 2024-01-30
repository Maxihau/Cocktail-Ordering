from ast import literal_eval
from bottle import request, Bottle, HTTPResponse
from DatabaseManagement import DatabaseManagement

app = Bottle()

# Access to both databases
order_queue = 'orderQueue.db'
request_queue = 'requestQueue.db'


@app.route('/', method='POST')
def order():
    form_data = request.forms
    form_data_dict = dict(form_data)
    callback_url = request.headers.get("CPEE-Callback")
    print(f"Callback URL: {callback_url}")
    print(f"Data dict: {form_data_dict}")
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

    filter = {
        'expr': expr,
        'item': item,
        'from': form_from,
        'to': form_to,
        'banned_users': banned_users_array,
        'callbackURL': callback_url
    }

    # Checks if anything in the order queue matches the new filter
    result = DatabaseManagement.process_data(order_queue, filter)
    # If yes, then send it right back
    if result is not None:
        DatabaseManagement.dequeue(order_queue, result["orderNb"])
        return result

    # If not, then add this filter into the request queue
    DatabaseManagement.create_filter(filter, request_queue)
    print("No result found. Send Callback")

    # Use callback function
    return HTTPResponse(status=200, headers={'CPEE-Callback': "true"})


if __name__ == "__main__":
    app.run(host="::", port=5123)
    # Local testing
    # app.run(host='localhost', port=8081, debug=True)

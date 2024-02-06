from ast import literal_eval
from bottle import request, Bottle, HTTPResponse, abort
from DatabaseManagement import DatabaseManagement, ItemRepository

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
    try:
        pattern_array = literal_eval(pattern)
        if not isinstance(pattern_array, list):
            raise ValueError("Pattern should be a list.")
    except (ValueError, SyntaxError):
        abort(422, "Invalid pattern format. Must be a list.")

    expr = pattern_array[0] if pattern_array else None
    items = pattern_array[1:] if len(pattern_array) > 1 else None
    for item in items:
        ItemRepository.add_item_to_itemsDB(item)


    # Optionally get 'from', 'to', and 'banned_users' fields
    form_from = request.forms.get('from', None)
    print(f"From: {form_from}")
    form_to = request.forms.get('to', None)
    print(f"To: {form_to}")

    # Convert 'banned_users' string to a list
    banned_users_str = request.forms.get('banned_users', '')  # default to '[]' if not provided
    banned_users_array = literal_eval(banned_users_str) if banned_users_str else None

    # Ensure that banned_users_array is a list of integers
    if banned_users_array is not None:
        banned_users_array = [int(user) for user in banned_users_array if
                              isinstance(user, (int, str)) and str(user).isdigit()]

    print(f"Banned users: {banned_users_array}")

    filter = {
        'expr': expr,
        'item': items,
        'from': form_from,
        'to': form_to,
        'banned_users': banned_users_array,
        'callbackURL': callback_url
    }
    filter = {key: value if value != '' else None for key, value in filter.items()}

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
    #app.run(host='localhost', port=8081, debug=True)

from ast import literal_eval
from bottle import request, Bottle, HTTPResponse, abort
from DatabaseManagement import DatabaseManagement, WordsRepository

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
    # Adds the words to the words database
    for item in items:
        WordsRepository.add_word_to_wordsDB(item)
    WordsRepository.add_word_to_wordsDB(expr)

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

    request_cpee = {
        'expr': expr,
        'item': items,
        'from': form_from,
        'to': form_to,
        'banned_users': banned_users_array,
        'callbackURL': callback_url
    }
    request_cpee = {key: value if value != '' else None for key, value in request_cpee.items()}

    # Checks if anything in the order queue matches the new request (from CPEE)
    result = DatabaseManagement.match_new_request(order_queue, request_cpee)
    # If yes, then send it right back
    if result is not None:
        DatabaseManagement.dequeue_order(order_queue, result["orderNb"])
        return result

    # If not, then add this filter into the request queue
    DatabaseManagement.enqueue_filter(request_cpee, request_queue)
    print("No result found. Send Callback")

    # Use callback function
    return HTTPResponse(status=200, headers={'CPEE-Callback': "true"})


if __name__ == "__main__":
    app.run(host="::", port=5123)
    # Local testing
    # app.run(host='localhost', port=8081, debug=True)

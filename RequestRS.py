from ast import literal_eval
import concurrent.futures
from bottle import request, Bottle
from DatabaseManagement import DatabaseManagement
import requests

app = Bottle()

# Access to both databases
orderQueue = 'orderQueue.db'
requestQueue = 'requestQueue.db'
executor = concurrent.futures.ThreadPoolExecutor()


def process_order_async(callback_url):
    try:
        result = DatabaseManagement.checkDatabaseEntry(requestQueue)
        # DatabaseManagement.process_data(orderQueue, data)
        print(f"Result found in RequestRS: {result}")
        resultWrapped = wrapToData(result)
        # print("Sending to CALLBACK URL")
        send_callback(callback_url, resultWrapped)

        # Handle the result, send a callback, etc.
        # You may want to handle callback_url here or in process_data itself
    except Exception as e:
        # Handle exceptions, log errors, etc.
        print(f"An error occurred: {e}")


def send_callback(callback_url, result):
    try:
        print("Trying to send to Callback-URL")
        response = requests.post(callback_url, json=result)
        response.raise_for_status()  # Raise an exception for bad responses (non-2xx)
        print(f"Callback Response: {response.text}")
        executor.shutdown()
    except requests.exceptions.RequestException as e:
        # Handle request exceptions
        print(f"Callback Request Error: {e}")


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
    executor.submit(DatabaseManagement.process_data(orderQueue, data))
    executor.submit(process_order_async, callback_url)

    return ''


def wrapToData(result):
    data = {
        'orderNb': result[0],
        'expr': result[1],
        'item': result[2],
        'userID': result[3],
        'timestamp': result[4]
    }
    return data


if __name__ == "__main__":

    #app.run(host="::", port=5123)
    app.run(host='localhost', port=8081, debug=True)

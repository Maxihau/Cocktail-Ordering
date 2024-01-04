from bottle import get, post, request, Bottle

import sqlite3

app = Bottle()
orderQueue = 'orderQueue.db'
requestQueue = 'requestQueue.db'

@post('/')
def order():
    content_type = request.headers.get('Content-Type')
    print("Received POST request with Content-Type:", content_type)

    # Access the form data
    form_data = request.form
    print("Received form data:", form_data)

    for header, value in request.headers.items():
        print(f"{header}: {value}")

    # Process the form data as needed
    # Example: print each key-value pair
    for key in form_data:
        print(f"{key}: {form_data[key]}")
    cpee_callback_url = request.headers.get('Cpee-Callback')

    data = {
        'cocktail': 'Negroni'
    }

    # Simulate sending back the data (for demonstration)
    return data

if __name__ == "__main__":
    #app.run(host="::", port=5123)  # Runs the application on port 5000
    app.run(host='localhost', port=8080, debug=True)
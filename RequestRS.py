from bottle import get, post, request, Bottle, route
from DatabaseManagement import DatabaseManagement

app = Bottle()

orderQueue = 'orderQueue.db'
requestQueue = 'requestQueue.db'

@app.route('/', method='POST')
def order():
    content_type = request.headers.get('Content-Type')
    print("Received POST request with Content-Type:", content_type)

    # Access the form data
    form_data = request.forms
    #print("Received form data:", form_data)
    form_data_dict = dict(form_data)

    #for header, value in request.headers.items():
    #    print(f"{header}: {value}")

    print(form_data_dict)
    
    # Process the form data as needed
    # Example: print each key-value pair
    #for key in form_data:
    #    print(f"{key}: {form_data[key]}")
    cpee_callback_url = request.headers.get('Cpee-Callback')

    data = {
        'orderNb': '',
        'user_id': '',
        'cocktail_name': ''
    }
    data_isEmpty = any(value == '' for value in data.values())

    while data_isEmpty:
        orderNb, user_id, cocktail_name = DatabaseManagement.dequeue(requestQueue)
        if cocktail_name is not None and user_id is not None and orderNb is not None:
            data['orderNb'] = orderNb
            data['user_id'] = user_id
            data['cocktail_name'] = cocktail_name
            data_isEmpty = False
            DatabaseManagement.databaseBalanceManagement()
            print(f"New Order: {cocktail_name} ordered by {user_id} with order number {orderNb}")
    return data

if __name__ == "__main__":
    app.run(host="::", port=5123)
    #app.run(host='localhost', port=8081, debug=True)
import requests
from bottle import request, Bottle, abort
from DatabaseManagement import DatabaseManagement, ItemRepository
from NumberTooBigError import NumberTooBigError


app = Bottle()
# Access to both databases
order_queue = 'orderQueue.db'
request_queue = 'requestQueue.db'


# Used when an HTTP is posted here
# Adds the order to the right queue (or database)
def add_item(expr, item, userID, timestamp):
    # Check the number of both databases
    numQueueRequest = DatabaseManagement.check_num_queue(request_queue)
    numQueueOrder = DatabaseManagement.check_num_queue(order_queue)

    # Checks if a cocktail is already in the request queue
    # If not, add it to the request queue
    # If yes, then add it to the order queue
    try:
        DatabaseManagement.enqueue(order_queue, -1, expr, item, userID, timestamp)
    except Exception as e:
        print(f"Error while trying to a an item: {e}")
        raise e


# Checks if the new input fulfills any filters in the RequestQueue
def matching(data):

    filters = DatabaseManagement.get_all_filters()
    for filter in filters:
        print("Checking one filter")
        processedFilter = DatabaseManagement.convert_filter_to_data(filter)
        result = DatabaseManagement.match_filter_data(processedFilter, data)
        if result:
            print("Result found in matching")
            DatabaseManagement.delete_filter_by_callback_url(filter[5])
            callback(data, filter[5])
            print(processedFilter)
            return True
    return False


def callback(result, callbackURL):
    headers = {'Content-Type': 'application/json'}
    response = requests.put(callbackURL, json=result, headers=headers)
    print(f"Response of Callback: {response}")


# Handles the POST Request
@app.route('/', method='POST')
def expr_item():
    data = request.json

    if 'expr' in data and 'item' in data and 'userID' in data and 'timestamp' in data:
        expr = data['expr']
        items = [data['item']] if ',' not in data['item'] else data['item'].split(', ')

        # for i in range(len(items)):
        #     items = checkItemSpelling(items)

        userID = data['userID']
        timestamp = data['timestamp']

        print(expr)
        print(items)
        print(userID)
        print(timestamp)


        try:
            for item in items:
                if not matching(data):
                    print("Added item to OrderQueue")
                    add_item(expr, item, userID, timestamp)
        except NumberTooBigError as e:
            print(e)
            abort(500, "There was an internal error with the database. Please check console")
        except Exception as e:
            print(e)
            abort(500, "Unknown error. Check server console")

        # Print the cocktail and the customer's name
        print(f"Expr {expr} with item(s): {items} requested by {userID} at time: {timestamp}")
        return ''
    else:
        abort(422, "Wrong data (format)")


# def checkItemSpelling(provided_item):
#
#     # Tokenize the provided item
#     provided_tokens = nlp(provided_item)
#
#     # Initialize variables to store the best match and its similarity score
#     best_match = None
#     best_similarity = 0.0
#
#     # Compare with each valid item
#     for valid_item in ItemRepository.get_all_valid_items():  # Implement get_all_valid_items() based on your data source
#         valid_tokens = nlp(valid_item)
#
#         # Calculate similarity between tokens
#         similarity = provided_tokens.similarity(valid_tokens)
#
#         # Adjust the similarity threshold based on your needs
#         if similarity > best_similarity:
#             # If similarity is above the threshold, update the best match
#             best_match = valid_item
#             best_similarity = similarity
#
#     # Return the best match (or the original item if no match is found)
#     return best_match if best_similarity > 0.7 else provided_item


if __name__ == "__main__":
    # Local testing
    app.run(host='localhost', port=8080, debug=True)
    #app.run(host="::", port=5321)

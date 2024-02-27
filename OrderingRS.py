import requests
from bottle import request, Bottle, abort
from DatabaseManagement import DatabaseManagement, WordsRepository
from fuzzywuzzy import fuzz

app = Bottle()
# Access to both databases
order_queue = 'orderQueue.db'
request_queue = 'requestQueue.db'


# Used when an HTTP is posted
# Adds the order to the right queue (or database)
def add_item(expr, item, userID, timestamp):
    # Checks if a cocktail is already in the request queue
    # If not, add it to the request queue
    # If yes, then add it to the order queue
    try:
        DatabaseManagement.enqueue_order(order_queue, -1, expr, item, userID, timestamp)
    except Exception as e:
        print(f"Error while trying to a an item: {e}")
        raise e


# Checks if the new input fulfills any filters in the RequestQueue
def matching(data, item):
    requests_cpee = DatabaseManagement.get_all_requests()
    for request_cpee in requests_cpee:
        print("Checking one filter")
        processed_request = DatabaseManagement.convert_request_to_data(request_cpee)
        result = DatabaseManagement.match_new_order(processed_request, data, item)
        if result:
            data['item'] = item
            print("Result found in matching")
            DatabaseManagement.dequeue_filter_by_callback_url(request_cpee[5])
            callback(data, request_cpee[5])
            print(processed_request)
            return True
    return False


# Calls back the CPEE tool via the callback-url
def callback(result, callbackURL):
    headers = {'Content-Type': 'application/json'}
    response = requests.put(callbackURL, json=result, headers=headers)
    print(f"Response of Callback: {response}")


# Handles the POST Request
@app.route('/', method='POST')
def expr_item():
    data = request.json

    if 'expr' in data and 'item' in data and 'userID' in data and 'timestamp' in data:
        data['expr'] = check_word_spelling(data['expr'])
        # User has to add a ',' between each item ordered
        # The items were already checked by the discord bot, therefore it should only be one of both cases
        if ',' not in data['item']:
            # If no comma is present, create a list with the item as the only element
            items = [check_word_spelling(data['item'])]
            data['item'] = items

        elif ',' in data['item']:
            # If a comma is present, split the item string into a list using ', ' as the delimiter
            items = data['item'].split(', ')
            corrected_items = []
            for item in items:
                print(f"(wrong) item name {item}")
                corrected_item = check_word_spelling(item)
                print(f"(corrected item name {corrected_item}")
                corrected_items.append(corrected_item)
            data['item'] = corrected_items
        else:
            abort(500, "Wrong input error. It seems that there were no items ordered")

        print(data['expr'])
        print(data['item'])
        print(data['userID'])
        print(data['item'])

        try:
            # Matching the item with the queued requests
            for item in data['item']:
                if not matching(data, item):
                    print("Added item to OrderQueue")
                    add_item(data['expr'], item, data['userID'], data['timestamp'])
        except Exception as e:
            print(e)
            abort(500, "Unknown error. Check server console")

        # Print the cocktail and the customer's name
        print(
            f"Expr {data['expr']} with item(s): {data['item']} requested by {data['userID']} at time: {data['timestamp']}")
        return ''
    else:
        abort(422, "Wrong data (format)")


# Checks the input item if it has a typo be crosschecking the words given in the database
# The wordsRepository comes from the incoming processing requests from CPEE (Assuming that the words from CPEE are correct)
def check_word_spelling(provided_word):
    # Initialize variables to store the best match and its similarity score
    best_match = None
    best_similarity = 0

    similarity_threshold = 70

    # Compare with each valid item using fuzzy string matching
    for valid_item in WordsRepository.get_all_valid_words():
        similarity = fuzz.token_sort_ratio(provided_word.lower(), valid_item.lower())

        # Adjust the similarity threshold based on your needs
        if similarity > best_similarity:
            # If similarity is above the threshold, update the best match
            best_match = valid_item
            best_similarity = similarity
            print(f"best match {best_match} and best similarity {best_similarity}")

    # Return the best match (or None if no match is found above the threshold)
    return best_match if best_similarity > similarity_threshold else provided_word


if __name__ == "__main__":
    # Local testing
    app.run(host='localhost', port=8080, debug=True)
    # app.run(host="::", port=5321)

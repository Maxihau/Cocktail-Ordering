# Cocktail ordering via Discord
The Cocktail Ordering system simplifies order processing through Discord, directing requests to the CPEE tool for order fulfillment. In instances where CPEE services are unavailable, the system intelligently queues orders. On the service end, the CPEE tool processes orders meeting specific criteria, with unmatched requests similarly queued until service availability.



## Usage

### Package dependencies:

The following packages are needed:

* sqlite3
* datetime
* requests
* bottle
* discord
* fuzzywuzzy
* ast

### Execution

First, there are 4 classes that need to be executed in order to run the whole system (The order of execution of the python classes is not important):
* Discord_BOT.py
* ItemReadyMessage.py
* OrderingRS.py
* RequestRS.py

When all instances are running, then create and execute an CPEE instance with the "Cocktail_template.xml" file in this repository (For more information, see CPEE Tool/ Instructions).

Now everything is ready to go!

The user now can send a direct message via Discord to the Discord bot with the Discord User ID "1184433277537366036".

The message must be structured by the following:

"!&lt;expression&gt; &lt;item1&gt;, &lt;item2&gt;, ..."
```
Example: 
!order Negroni, Old Fashioned
```
Both items in this case will then be ordered

### CPEE Tool

The CPEE tool is modular, service oriented workflow execution engine (For more information, see https://cpee.org/). In this case, it handles the processing of cocktails by sending the requests that it is available to process a new order. It can also set up criteria which need to be fulfilled before sent to it (For more information, see Features/ Criteria filtering).

#### Instructions

* Open https://cpee.org/ and start a "Demo" on the left navigation bar
* Then create a new instance (right side) and monitor the instance
![Screenshot create instance.png](Screenshots%2FScreenshot%20create%20instance.png)
* When redirected, the CPEE tool should show up. Now it is important to use the template given in this repository by loading the testset and open the "Cocktail_template.xml" file
![Screenshot Template.png](Screenshots%2FScreenshot%20Template.png)
* A process model should now show up
* Now it is possible to change the criteria according to the liking under "Properties/ Arguments"
* It is important to write the criteria in the right format:
  * pattern: 
    * The pattern contains at least one string. The first string is the expression which should be in the incoming orders
    * Everything after are items that it can process, e.g. machine can make Negroni and Old Fashioned (See screenshot below)
    * If not, it should at least have the expression
      * Example ``` ["order"]```
    
    * The overall structure looks like this
      
      ```[<expr>, <item1>, <item2>, ...]```
  * from/ to:
    * Correct format: ```hh:mm```
  * banned users:
    * It is an array of numbers (Discord IDs only contain numbers)
    * Format:
      * Empty: ```[]``
      * Not Empty: ```[123434412, 231231241]```

![Screenshot Criteria.png](Screenshots%2FScreenshot%20Criteria.png)
* After that go to the Execution tab up which is at the top of the website
![Screenshot Execution.png](Screenshots%2FScreenshot%20Execution.png)

## Features

There are some features that streamline the whole ordering process:

* The user can order more than one cocktail, and they will be seen as individual orders
* The system checks the typos in the order from the user and corrects them based on its database (The data is based on the service calls from the CPEE tool, assuming that they are correct)
* (A)synchronous ordering:
  * When an instance is ready, an order is placed, and it matches its criteria, then the order will be immediately processed without being queued. 
  * When an instance is still busy with one order and the user orders an item, the order is still saved in a queue and will be processed when the instance is ready. The user then doesn't have to reorder again.
* (A)synchronous service:
  * When an instance is ready again and there is an order in the queue that matches its criteria, then the order will be processed immediately without saying that it is ready for orders. 
  * When an instance is ready but there a no orders available to process, the instance sends a callback-url to process the upcoming orders (If the order matches the criteria).
* Criteria filtering:
  
  The instance has a few filtering criteria to only process the orders the CPEE instance wants to. It can be setup in the Properties/ Arguments in the service call (See template).
  * Expression: The expression from the order has to match the expression from the CPEE instance.
  * Item: If each of the ordered item from the user matches with the item(s) that the CPEE instance supports.
  * From: The instance limits the time from when it wants to process the order. Every order before that will be ignored.
  * To: The instance limits the time until when it wants to process the order. Every order before that will be ignored.
  * Banned users: The instance ignores orders from users that are blacklisted.

## Technical Background  
In the following, each class will be described and explained clearly. The main clustered components consist of the system (RequestRS.py, OrderingRS.py & DatabaseManagement.py), Discord system (Discord_BOT.py & ItemReadyMessage.py) and CPEE (Processing the order).

### DatabaseManagement.py

This python file contains all the needed functions that are related to the database handling by using the SQlite3 Library. Two different classes handle the database:

#### DatabaseManagement

This is the main class that saves and processes the incoming requests from both the CPEE instance and the user when needed into the database (As a queue). It also matches both requests with each-other when needed.

All functions are static methods which then are called by the other classes when needed.

##### Methods

* **enqueue_filter**: When a service request (via CPEE) is made but there is no matching order to execute. The service (including the callback-url) is then saved in the queue of the database in order to be processed later.
* **convert_filter_to_data**: Is needed to convert the data from the database into the needed format to match it with the data from the order.
* **get_all_functions**: Get all the queued services/ requests from CPEE that are available.
* **match_new_filter**: Tries to match the new request with the already existing orders in the database.
* **warp_to_data**: Wraps an array to a dictionary.
* **dequeue_filter_by_callback_url**: Deletes the selected service request with the given callback url as it is unique.
* **match_new_order**: When a new order is placed, the function checks if it matches with any service requests.
* **get_max_order_number**: Needed to create a new order with the upcoming order number. It is important to process the orders in the right numerical order.
* **enqueue_order**: Enqueues the order when there is no service request available at the moment by saving it in the database
* **dequeue_order**: Dequeues the order by the order number and returns it

#### WordsRepository

This class is needed to check the spelling of the words from the user's order as it might contain typos. Therefore, a list of known words from the service requests will be saved, assuming they are right.

##### Methods

* **add_word_to_wordsDB**: Add one word from the service call into the database.
* **get_all_valid_words**: Returns all words from the database to then be checked if it there checked words contain a typo.

### Discord_BOT.py

This class uses the Discord API and the Requests library. It handles the incoming messages from the user via Discord and sends the data(as a payload) to the OrderingRS.

##### Methods

* **on_ready**: Just prints to say that the Discord bot is online
* **on_message**: Processes the message and forwards it to the OrderingRS. Also checks if the message is syntactically right.

### OrderingRS.py

This class processes the incoming orders which were redirected by the Discord bot. It handles the input by checking for spelling, then checks if the already existing requests from CPEE matches with the one item of the order or not. 
* If yes, then each matched item is sent via the callback-url and then being processed.
* If not, then it will be enqueued into the order database.

Used libraries, frameworks: "requests", "bottle", "fuzzywuzzy" (String matching)

##### Methods

* **add_item**: Adds the item to the ordering queue in the database by using the function "enqueue_order(...)" in DatabaseManagement.
* **matching**: Checks if the selected item matches with any service requests from the request database.
* **callback**: Calls back the CPEE tool via the callback-url with the needed data.
* **expr_item**: Processes the incoming POST function from the Discord bot. First, it checks the strings if they contain any typos and corrects them, if needed. Then it calls the functions which try to match each item ordered and adds them into the database if needed.
* **check_word_spelling**: Compares the incoming word with the words form the database and if they are similar enough, they will then be replaced with the right one (Assuming the words are already saved in the database. These words come from the service requests from CPEE, which should be right).

### RequestRS.py

This class receives the incoming service requests from CPEE and processes it. There are two cases (Just like the OrderingRS):

* There is an order that matches the service request and can be synchronously sent back.
* There is no order that matches the service request. It will then be enqueued in the database with the callback url and then accessed when a new match is there.

Used libraries, frameworks: "bottle", "ast" ("literal_eval" to check if the input is right)

##### Methods

* **order**: The main function of this class. It checks first the data and if it is syntactically correct. Then adds the words into the database which later will be used to check for spelling (See OrderingRS.py/ check_word_spelling). It then checks if the new request matches with any orders. Either it sends back an order or sends a confirmation for the callback url and enqueues the request into the database.

### ItemReadyMessage.py

When the CPEE tool is done processing the order, it notifies the user by using this service. This class uses the Discord API and sends (with the same bot) a message to the user that the item is ready to be picked up.

Used libraries, framewords: "bottle", "Discord API", "requests"

##### Methods

* **send_discord_message**: Handles the POST request from the CPEE tool with the user id and the processed item. It uses the functions "create_dm_channel(...)" and "send_message(...)". 
* **create_dm_channel**: It establishes a dm channel in order to send a message. 
* **send_message**: Sends the actual message to the user.












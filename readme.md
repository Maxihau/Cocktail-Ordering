# Cocktail ordering via Discord
The Cocktail Ordering system simplifies order processing through Discord, directing requests to the CPEE tool for order fulfillment. In instances where CPEE services are unavailable, the system intelligently queues orders. On the service end, the CPEE tool processes orders meeting specific criteria, with unmatched requests similarly queued until the next order.

# Table of Contents


1. [Usage](#usage)
   - [Package Dependencies](#package-dependencies)
   - [Execution](#execution)
2. [Features](#features)
3. [CPEE Tool](#cpee-tool)
   - [Instructions](#instructions)
4. [Example Procedure](#example-procedure)
   - [Overview](#overview)
   - [Data Elements](#data-elements)
   - [Endpoints](#endpoints)
   - [Process Model](#process-model)
5. [Technical Background](#technical-background)
   - [DatabaseManagement.py](#databasemanagementpy)
      - [Database Management](#database-management)
      - [Words Repository](#words-repository)
   - [Discord_BOT.py](#discordbotpy)
   - [OrderingRS.py](#orderingrspy)
   - [RequestRS.py](#requestrspy)
   - [ItemReadyMessage.py](#itemreadymessagepy)

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

Before executing, please add your Discord token into the "Discord_Token.txt" file in the repository in order to work. (To create a Discord Token, see this [instruction](https://github.com/reactiflux/discord-irc/wiki/Creating-a-discord-bot-&-getting-a-token))

Execute the following classes in any order:
* Discord_BOT.py
* ItemReadyMessage.py
* OrderingRS.py
* RequestRS.py

Once all instances are running, create and execute a CPEE instance using the "Cocktail_template.xml" file in this repository (For detailed instructions, refer to [Instructions](#instructions)).

The system is now ready for use!

The user now can send a direct message via Discord to the Discord bot with the Discord User ID "1184433277537366036".

The message must be structured as follows:

"!&lt;expression&gt; &lt;item1&gt;, &lt;item2&gt;, ..."
```
Example: 
!order Negroni, Old Fashioned
```
Both items in this case will then be ordered

Example with **typos**:

![Screenshot Example.png](Screenshots%2FScreenshot%20Example.png)

## Features

There are some features that streamline the whole ordering process:

* Users can order multiple cocktails, and each is treated as an individual order.
* The system checks for typos in user orders and corrects them based on its database, derived from service calls by the CPEE tool.
* (A)synchronous ordering:
  * Orders are processed immediately if an instance is ready, matching criteria without queuing.
  * Orders are queued if an instance is busy, and processed when ready, eliminating the need for users to reorder.
* (A)synchronous service:
  * When an instance is ready, it processes queued orders matching criteria immediately.
  * If an instance is ready but no orders are available, it sends a callback URL for upcoming orders matching criteria.
* Criteria filtering:
  
  The instance has filtering criteria to process specific orders. These criteria can be set up in the Properties/ Arguments in the service call (See template).
  * Expression: The order expression must match the CPEE instance expression.
  * Item: Each ordered item must match the supported items of the CPEE instance.
  * From: Limits the time for processing orders.
  * Banned users: Ignores orders from blacklisted users.

## CPEE Tool


The CPEE tool is a modular, service-oriented workflow execution engine (More information: <a href="https://cpee.org/" target="_blank">CPEE</a>). It handles cocktail processing by indicating its readiness to process new orders. The tool can set up criteria that must be met before processing orders (Refer to Features/ Criteria filtering).

### Instructions

* Open https://cpee.org/ and start a "Demo" on the left navigation bar.
* Create a new instance on the right side and monitor the instance.
![Screenshot create instance.png](Screenshots%2FScreenshot%20create%20instance.png)
* When redirected load the testset and open the "Cocktail_template.xml" file from this repository.
![Screenshot Template.png](Screenshots%2FScreenshot%20Template.png)
* A process model should now show up.
* Customize the criteria under "Properties/ Arguments" according to preferences under "Properties/ Arguments".
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
      * Empty: ```[]```
      * Not Empty: ```[123434412, 231231241]```

![Screenshot Criteria.png](Screenshots%2FScreenshot%20Criteria.png)

Proceed to the Execution tab to process orders.

![Screenshot Execution.png](Screenshots%2FScreenshot%20Execution.png)


## Example procedure
This chapter shows a detailed example of the process model in CPEE. This should be a guideline for a better understanding of processing and handling the data.

### Overview

![Screenshot CPEE overview.png](Screenshots%2FScreenshot%20CPEE%20overview.png)

Looking at the template the process shows the making of two cocktails. The first two column represents one cocktail (Negroni & Daiquiri) and the third one is the default one.

When using the CPEE tool, there are two important tabs that needed to be viewed before.

### Data Elements

![Screenshot Data Elements.png](Screenshots%2FScreenshot%20Data%20Elements.png)

Data Elements are the variables that save the data from service calls with scripts. Here, the item is a Daiquiri and the user_id is 12342314331431 (For storing the data, see [Process Model](#process-model))

### Endpoints

![Screenshot Endpoints.png](Screenshots%2FScreenshot%20Endpoints.png)

This tab is important for the communication via REST services. The links are saved in this tab and labeled. Here is an example for the variables "getOrder" and "sendMsg". In this case, the ports are active from the python classes and are waiting for a request.

### Process Model

This chapter explains the whole process model of the "Cocktail_template.xml"

![Screenshot Service Call Start.png](Screenshots%2FScreenshot%20Service%20Call%20Start.png)

This service call with scripts is the main part of this process model. It is important to set the endpoint to "getOrder" as we need the link to use the POST method with the arguments shown in the figure. The arguments set up the criteria which need to be met to accept this order (See figure, Properties/ Arguments) and receives the ordered item and the user (See figure, Output Handling/ Finalize). It is important to note that a callback url is also sent to the endpoint. This callback url can be used to wait for a asynchronous messages.
Either the process model receives a synchronous message with the needed data or a response with the header "CPEE-callback" needs to be true (For code, see "RequestRS.py", line 74) which results into waiting for a post request via the callback url.

![Screenshot Service call: Output Handling.png](Screenshots%2FScreenshot%20Service%20call%3A%20Output%20Handling.png)

The data is then saved in the "Data Elements" tab (See [Data Elements](#data-elements)) for later sending messages to the user.

![Screenshot if-statement.png](Screenshots%2FScreenshot%20if-statement.png)

In order to make the cocktail, if statements are needed to create procedures as each cocktail needs different ingredients.
In this case, there are two columns with if conditions and a default column for everything else. The first column contains a if statement for the cocktail "Negroni".

![Screenshot Service Call Send Message.png](Screenshots%2FScreenshot%20Service%20Call%20Send%20Message.png)

Once a negroni is ordered, the condition gets true and starts making the cocktail. For each process, there will be a service call with a script. This script sends updates to the user. The example in the figure above shows a service call with script which adds gin into the glass and sends the message "Adding Gin" to the user. It is important to note that the Endpoint "sendMsg" is sent, the Method is a "post" request and the right arguments are set.

![Screenshot Service call ending.png](Screenshots%2FScreenshot%20Service%20call%20ending.png)

Once the whole cocktail making process is done, there will be one final service call which notifies the user that the cocktail is ready to be picked up. Example: Sends the user the message "Negroni is ready!".

After this service, the loop starts again at the first service call and posts a request for the next order until the execution is stopped and/ or terminated.

## Technical Background
In the following, each class will be described and explained clearly. The ordering system consist of the following components (RequestRS.py, OrderingRS.py & DatabaseManagement.py), Discord system (Discord_BOT.py & ItemReadyMessage.py) and CPEE (Processing the order).

### DatabaseManagement.py

This python file contains all the needed functions that are related to the database handling by using the SQlite3 Library. Two different classes handle the database:

#### Database Management

This is the main class that handles all the database related tasks. It saves, fetches, deletes data from the databases.

All functions are static methods which then are called by the other classes when needed.

##### Methods

* **enqueue_filter**: Saves a service request in the queue when no matching order is available.
* **convert_filter_to_data**: Converts database data into the format needed to match with order data.
* **get_all_functions**: Retrieves all queued service requests from CPEE.
* **match_new_filter**: Tries to match a new request with existing orders in the database.
* **warp_to_data**: Wraps an array into a dictionary.
* **dequeue_filter_by_callback_url**: Deletes a service request with the given callback URL.
* **match_new_order**: Checks if a new order matches any service requests.
* **get_max_order_number**: Retrieves the maximum order number for processing orders in the correct numerical order.
* **enqueue_order**: Saves an order in the database queue when no service request is available.
* **dequeue_order**: Retrieves and dequeues an order by order number.

#### Words Repository

This class checks the spelling of words in user orders against known words from service requests, assuming they are correct.

##### Methods

* **add_word_to_wordsDB**: Adds a word from a service call to the database.
* **get_all_valid_words**: Retrieves all words from the database to check for typos.

### Discord_BOT.py

This class uses the Discord API and the Requests library to handle incoming messages from users via Discord, forwarding data to OrderingRS.

##### Methods

* **on_ready**: Just prints to say that the Discord bot is online
* **on_message**: Processes messages, forwards them to OrderingRS, and checks for syntax correctness.

### OrderingRS.py

This class processes incoming orders redirected by the Discord bot. It checks spelling and matches existing CPEE requests with ordered items. It either sends matched items via the callback URL for processing or enqueues unmatched orders.

Used libraries, frameworks: "requests", "bottle", "fuzzywuzzy" (String matching).

##### Methods

* **add_item**: Adds the item to the ordering queue in the database using the function "enqueue_order(...)" in DatabaseManagement.
* **matching**: Checks if a selected item matches any service requests in the database.
* **callback**: Calls back the CPEE tool via the callback URL with the necessary data.
* **expr_item**: Processes the incoming POST function from the Discord bot, checking strings for typos and calling functions to match and add items to the database if needed.
* **check_word_spelling**: Compares incoming words with words from the database and replaces them if similar enough (Assumption: There is an error)

### RequestRS.py

This class receives incoming service requests from CPEE and processes them. It handles cases where there is a matching order for synchronous processing or enqueues requests with callback URLs for later processing.

Used libraries, frameworks: "bottle", "ast" ("literal_eval" to check if the input is right).

##### Methods

* **order**: The main function checks the data for syntax correctness, adds words to the database for spelling checks (See [OrderingRS](#orderingrspy) / check_word_spelling), and processes requests by either sending back an order or confirming the callback URL and enqueuing the request.

### ItemReadyMessage.py

This class notifies users when the CPEE tool has completed order processing. It uses the Discord API to send a message to the user, utilizing the same bot.

Used libraries, framewords: "bottle", "Discord API", "requests".

##### Methods

* **send_discord_message**: Handles the POST request from the CPEE tool with the user ID and processed item. It uses functions "create_dm_channel(...)" and "send_message(...)".
* **create_dm_channel**: Establishes a DM channel to send a message.
* **send_message**: Sends the actual message to the user.












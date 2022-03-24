# spending_challenge

# Summary
The Expense Tracker enables you to keep track of your expenses. The service provides
functionalities to register spendings and retrieve a collection of past entries.
The expenses can be filtered by the supported currencies (to date, USD and HUF) and sorted
by the amount value of the time of registration.

# Endpoints
The Service supports the following public endpoints:
- / (root) [GET, POST] provides a registration form for new expenses; lists past expenses,
                       offering filtering by currency and sorting by time or by amount.
- /spendings [GET] returns a batch JSON collection of expenses. The same filtering and
                   sorting applies as above.
- /add_spending [POST] JSON supported programmatic way of entering new expenses

# Run the service (from root folder)
install the necessary dependencies:
$ pip install -r requirement.txt
configure the service host and port (or rely on default values).
$ python3.7 app.py --host localhost --port 5000

# Testing
- (limited) unit testing available under tests.py:
$ pytest -sv tests.py

- curl-based programmatic testing of the batch endpoints:
$ curl http://127.0.0.1:5000/spendings
$ curl -X POST -d '{"amount":1200,"currency":"USD","description":"Mango",    "spent_at":"2022-02-23T14:47:20.381Z"}'\
      -H 'Content-Type: application/json' http://127.0.0.1:5000/add_spending

# Performance
The service is handled by a high-performing gevent-based WSGI server.
The service assumes an equal load of [POST](/add_spending) and [GET](/, /spendings) request. This assumption is supported by the fact that every newly entered spending should be displayed.

The data-layer of the application stores and updates SORTED collections of the expenses, hence no query-time sorting is necessary, keeping the complexity of the operations linear (wrt the data size).

# Proposal of additional work and feature improvements:
- Enable persistent storage:
while the problem proposal mentions an SQL storage layer, per email discussion we have established that expenses with identical properties might be entered on multiple occasions. Hence the choice of an SQL db might be suboptimal due to the burden of private-key choosing.
We could introduce a "count" property to circumwent the above difficulties. Alternatively, a non-SQL db could serve our purposes (such as Redis with independent keys and sorted sets for every collection).

- Enrich the service with additional features such as:
   -> sum of expenses per currencies
   -> enable the UI to modify or remove expenses from the db

- Additional unit testing:
The presented unit tests verify the main functionalities but do not provide an exhaustive
coverage of all functionalities. Within the scope of the project, manual testing was put into
practice to verify the accurate behavior of the service.
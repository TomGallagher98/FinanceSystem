# FinanceSystem

Fincance System assignment created for Distributed Systems class as part of the Informatics Bachelor course at IMC FH Krems

File Description
Authenticate_Rest.py
Exposes API on port 5000
Provides services for Logging users in, checking the validity of a user that is trying to access a resource and Adding or Removing Users from the system
Also responsible for the creation of the database

DataService_Rest.py
Exposes API on port 8080
Provides services for creating jobs via the POST request and updating jobs via the PUT request 
Authentication of users is done via the authentication service
The PUT and POST requests both perform the function of updating the jobs table with the inputted information from the user and forwading the job to the 
message service.
Data is validated using regex expressions.

MessageService.py
Exposes API on port 7500
Provides a message queue service for storing jobs between the data service and calculation service.
Jobs are added to queues via POST calls from the data service and fetched from the queues by the calculation service via GET calls
The state of the queues is persristed via pickle dumps which can be loaded upon startup in the case of the service crashing.
A service for managing queues and the distribution of jobs between queues is also provided
It ensures that if a new queue is added the jobs are distributed in order of when they were originally uploaded.

CalculationService.py
Predicts a value based on the assets provided via a series of timeseries regression models.
Tasks are distributed between processors via message passing interfaces. The number of processors is defined upon startup.
The assets of each job are distributed to the processors which then create a prediction based on the created timeseries models.
They are then returned and averaged to create an overall prediction
The final result is returned to the message service.

Client_Rest.py
The client for the application
Provides services for a user to login, request to perform tasks and input job information

timeseries.py
Code provided by lecturer Ruben Ruiz Torrubiano

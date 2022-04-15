# FinanceSystem

I chose to use the Rest Framework because it was useful for creating bidirectional Clients/Servers. It was easy to expose APIs between the servers so that each server could access the features on the separate servers.
It was also useful for defining the commands (GET, PUT, PUSH, DELETE) in a straightforward manner. Each call could be updated in the same fashion so it allowed for relative consistency within the code.

File Description
Authenticate_Rest
The authentication service, this ended up being the biggest file as it had the most features that needed to be used in the initial stages.
It contains 3 resources: The login service, a resource for checking that tokens are valid and a resource to manage users
The Login Service, takes data sent by the client and accesses the SQLite database to check if the user is in the database. 
If the user is valid, the service then generates a random token, which is returned to the Client. It is also saved into a Python Dictionary along with the username, timestamp and user group. 
The Token Checker is used to verify whether a user has access to certain features within the System and whether or not a token is still valid within the session.
It checks that the token has not been in use for more than a specified amount of time (100 seconds in the code but realistically would be longer) using the check time function
The resource also checks that a user has permission to perform a job, this is done with the validate job function. It takes the users position and the job being performed (which is sent with the job request) and checks that they are authorized to perform the task.
The Token checker is also used to log users out at the end of a session. When a client requests to logout, the service removes their token from the token dictionary
The Manage Users service is a service available to the administrators. It allows them to add and remove users into the SQLite Database. It takes the username, password and user group from the client and then writes it into the database using a sqlite command.
Users can also be deleted using the service, the client only needs to provide the username, since it is a primary key it must be unique. Then a SQLite query is used to remove the user from the database

Client_Rest
Is the main user interface of the system. It uses a while loop to take input from the user, with 3 states (x = 0,1,2)
x = 0 allows the user to access the login and main page, x = 1 allows the user to access only the login page (it is set to 1 when incorrect login details are provided), x = 2 is used to exit the program entirely.
It uses a basic while loop system, the inputs are parsed by the system and if they match with a command provided by the system they system then connects to the relevant API needed to perform the service.
For services that require extra input the user is again prompted to enter the input via the console.

DataService_Rest
The master data service. It is the main connection to the database. It only contains one resource, the Master Data resource, which allows clients to Get Results, Update Jobs (Put) and Post Jobs
For each API call to the service the Client must add also add the additional data to use the service. Which will then be interpreted by the service when the business logic is fully implemented.
Get is used to allow clients to fetch results from the database, the user needs to add the job id which they want to access
Put is used for clients to update jobs, they will need the job id. When I have a better idea of how the feature is used I will update the code, for example if there should be a second api exposed depending on the type of update that needs to be made.
Post is used to create new jobs. The client inputs only the assests at the moment, again when I can update the business logic this might change 
Before allowing a user to access each service the data service first connects to the Authentication Service via the check token API to verify that the user has access to the resource.

For logging I have used "werkzeug" as it is the main for loggin flask applications. I used the original format for logging the main exchanges between the services but also added extra info to log the messages and metadata being sent between the services

I am using an SQLite database to manage all of the data for the project, queries are done using the SQLite3 framework in python

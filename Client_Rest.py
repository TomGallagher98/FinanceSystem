from requests import put, get, post, delete, exceptions
import logging

from suds.client import Client, WebFault

logging.basicConfig(level=logging.INFO, filename='log/finance.log')
logging.getLogger('werkzeug').setLevel(logging.DEBUG)
logging.getLogger('werkzeug').setLevel(logging.INFO)

token = ''
user = ''
# Using x = 0,1 or 2 instead of True or False
# if a user is logged out because their session ends/token is invalid they will be taken to the login page
# if a user quits the entire program will be quit (x = 2)
x = 0
while x == 0 or x == 1:
    try:
        print('Welcome Enter Username and Password')
        u_name = input('Username: ')
        p_word = input('Password: ')
        token = get('http://localhost:5000/login/api/',
                    json={'user': str(u_name), 'password': str(p_word)}).json()
        # Log = get source, dest = localhost:5000/login/api/, header = put, message = json{}
        x = 0
        print(token)
        if token == {'message': 'Invalid Login Details'}:
            print(token['message'])
            x = 1

        if x != 1:
            print('\n Welcome ' + u_name + '! \n')

        while x == 0:
            # Basic user interface, user inputs commands and the system checks if the are valid tasks
            # If not the user is prompted to input another command
            task = input('Enter Command: ')
            try:
                # For batch jobs, the user inputs the assets which will be used for the job
                if task == 'batch':
                    # Will update when I have more information on how the assets will be used by other services
                    assets = input("Please enter data values: ")
                    data = post('http://localhost:8080/Master_Data/api/',
                               json={'user': u_name, 'job': 'Batch', 'token': token['token'], 'assets': assets}).json()
                    if data['message'] != 'Job started':
                        print(data)
                    else:
                        # Enter job requirements
                        print(data)
                # The user inputs the job id that they wish to view
                if task == 'results':
                    job_id = input('Which job would you like data from: ')
                    data = get('http://localhost:8080/Master_Data/api/',
                               json={'user': u_name, 'job': 'Result', 'token': token['token'], 'job_id': job_id}).json()
                    if data['Error']:
                        print(data)
                    else:
                        print(data)
                # The user inputs the id of the job they wish to update
                # Will add more features later such as type of update when I know more
                if task == 'update':
                    job_id = input('Which job would you like data from: ')
                    data = get('http://localhost:8080/Master_Data/api/',
                               json={'user': u_name, 'job': 'Update', 'token': token['token'], 'job_id': job_id}).json()
                    if data['Error']:
                        print(data)
                    else:
                        # Data to update
                        print(data)
                # For secretaries, I will add more features when I know what tasks secretaries can perform
                if task == 'data':
                    data = get('http://localhost:5000/Master_Data/api/',
                               json={'user': u_name, 'job': 'Data', 'token': token['token']}).json()
                    if data['Error']:
                        print(data)
                    else:
                        print(data)
                # For administrators, allows them to add users into the database
                if task == 'add_user':
                    data = get('http://localhost:5000/check_token/api/' + token['token'],
                               json={'user': 'Tom', 'job': 'add_user'}).json()
                    if data['message'] != 'Valid':
                        print(data)
                        x = 1
                    else:
                        username = input('New Username: ')
                        p_word = input('Password: ')
                        u_group = input('User Type: ')
                        new_user = post('http://localhost:5000/manage_users/api/',
                                        json={'user': username, 'password': p_word,'user_group': u_group}).json()
                # Allows administrators to remove users from the database
                if task == 'delete_user':
                    data = get('http://localhost:5000/check_token/api/' + token['token'],
                               json={'user': 'Tom', 'job': 'delete_user'}).json()
                    if data['message'] != 'Valid':
                        print(data)
                        x = 1

                    else:
                        username = input('Enter user to delete: ')
                        checker = input('Are you sure you want to delete user ' + username + '? [Y/n] ')
                        if checker == 'Y':
                            remove = delete('http://localhost:5000/manage_users/api/',
                                            json={'user': username}).json()
                        else:
                            continue

            except(exceptions.ConnectionError):
                print("Oops! Something went wrong!")

            finally:
                # Logs the user out of the session
                if task == 'quit':
                    message = delete('http://localhost:5000/end_session/api/' + token['token']).json()
                    if message == {'message':'logging out, goodbye'}:
                        print('Goodbye')
                        x = 2
                    else:
                        print(message)
                        print('Logout failed. Please try again')


    except (exceptions.ConnectionError):
        print("""\
                Ooops! Something went wrong!
                Please make sure to start the server first
            """)







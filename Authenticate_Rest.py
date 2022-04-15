from datetime import datetime
from flask import Flask, request
from flask_restful import Resource, Api
import logging
import sqlite3
import random
import string

app = Flask(__name__)
api = Api(app)

tokens = {}


def create_database():
    # Will be run if the database is not detected
    # The Authentication service is the first point of access, so I am using it to create the entire database
    # All other database access will be done by resources which require specific access to tables
    conn = sqlite3.connect("Finance_System.db")
    cursorObject = conn.cursor()
    cursorObject.execute("""CREATE TABLE Users(username text PRIMARY KEY UNIQUE,
                          password text,
                          user_group text
                          )""")

    cursorObject.execute("""CREATE TABLE Jobs(id integer PRIMARY KEY,
                          user text,
                          time timestamp,
                          status text,
                          daterange text,
                          assets integer)""")

    cursorObject.execute("""CREATE TABLE Results (id integer PRIMARY KEY,
                              jobID integer,
                              time timestamp,
                              assets integer)""")

    conn.commit()

class LoginService(Resource):
    def get(self):
        data = request.json
        user = data['user']
        password = data['password']

        # Tries to create a database/checks that the database exists
        try:
            create_database()
        except sqlite3.Error as e:
            print (e)

        # Searches for a matching username and password, logs the user in if it matches
        conn = sqlite3.connect("Finance_System.db")
        cursorObject = conn.cursor()
        cursorObject.execute("SELECT * from Users WHERE username = :u and password = :p",{"u": user, "p": password})
        login = cursorObject.fetchall()
        if len(login) > 0:
                token = generate_token()
                time = get_current_time()
                tokens[token] = {'user': user, 'user_group': login[0][2], 'login_time': time}
                print(tokens[token])
                app.logger.info({'message': user + ' successfully logged in'})
                return {'token': token}
        else:
            message = {'message': 'Invalid Login Details'}
            app.logger.info(message)
            return message


def generate_token():
    # Creates a random token between 15 and 20 characters
    length = random.randint(15, 20)
    letters = string.ascii_letters
    digits = string.digits
    punctuation = "-._~"  # Only characters that can be used in a url, tokens are used as part of api calls later on
    choices = ''.join((letters, digits, punctuation))
    token = ''.join(random.choice(choices) for i in range(length))
    print(token)
    return token


def get_current_time():
    # Splits the datetime time stamp into seconds
    current = str(datetime.now())
    current = current.split(' ')[1]
    current = current.split('.')[0]
    current = current.split(':')
    c_sec = int(current[0]) * 60 * 60 + int(current[1]) * 60 + int(current[2])
    return c_sec


class TokenChecker(Resource):
    def get(self, token):
        data = request.json
        job = data['job']
        user_group = tokens[token]['user_group']
        # check token is valid, check user is valid, return user group
        # Check if the token is in the token list
        if token not in tokens:
            app.logger.info({'message': 'Token not valid'})
            return {'message': 'Token not valid'}
        # Checks that the token has not been in use for too long
        if check_time(tokens[token]['login_time']) != 'Valid':
            tokens.pop(token)
            app.logger.info({'message': 'Session Time Out'})
            return {'message': 'Session Time Out'}
        # Checks that the user has the permission to perform the job
        if validate_job(job, user_group) == 'Invalid':
            app.logger.info({'message': 'Access Denied'})
            return {'message': 'Access denied. You do not have permission to access resource'}
        else:
            app.logger.info({'message': 'Permission Granted'})
            return {'message': 'Valid'}


def check_time(login_time):  # Change to factor in date
    # checks that the user is still within their session time
    # session time would theoretically be longer ~ 6 hours, I kept it shorter for validation purposes
    current = get_current_time()
    if current - 100 > login_time:
        return {'message': 'Session timed out'}
    else:
        return 'Valid'


def validate_job(job, user_group):
    # Might update this code as user jobs become more clear
    # Batch, Results, Data
    # Checks a user group is able to perform the task they are requesting
    if user_group == 'administrator':
        # Administrators have access to all privileges so no need to check further
        return 'Valid'
    if user_group == 'manager':
        # Managers can submit Batch Jobs and gather Results
        if job == 'Batch' or job == 'Result' or job == 'Update':
            print(job)
            return 'Valid'
    if user_group == 'secretary':
        # Secretaries can only manage some data
        if job == 'Data':
            return 'Valid'
        else:
            return 'Invalid'
    else:
        return 'Invalid'


class TokenDeleter(Resource):
    # Logs a user out of a session at their request
    def delete(self, token):
        if token in tokens:
            tokens.pop(token)
            app.logger.info({'message': 'Logged out'})
            return {'message': 'logging out, goodbye'}
        else:
            # if token is not in list the user will also be logged out, so message stays the same
            # This is more for error handling
            app.logger.info({'message': 'Logged out '})
            return {'message': 'logging out, goodbye'}


class ManageUsers(Resource):
    def get(self, user):
        return user
    def post(self):
        user = request.json['user']
        password = request.json['password']
        user_group = request.json['user_group']

        conn = sqlite3.connect('Finance_System.db', timeout=10)
        cursorObj = conn.cursor()

        cursorObj.execute(
            f'INSERT INTO Users VALUES(:u, :p, :ug)',
            {"u": user, "p": password, "ug": user_group})
        conn.commit()
        app.logger.info({'message': 'Added user ' + user})
        return user

    def delete(self):
        user = request.json['user']
        conn = sqlite3.connect('Finance_System.db', timeout=10)
        cursorObj = conn.cursor()
        cursorObj.execute(
            f'DELETE FROM Users WHERE username = :u',{"u":user}
        )

        app.logger.info({'message': 'Removed User' + user})


api.add_resource(TokenChecker, '/check_token/api/<string:token>')
api.add_resource(LoginService, '/login/api/') # Maybe will add user group for admin service
api.add_resource(TokenDeleter, '/end_session/api/<string:token>')
api.add_resource(ManageUsers, '/manage_users/api/')

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, filename='log/finance.log')
    logging.getLogger('werkzeug').setLevel(logging.DEBUG)

    app.run(debug=True, port=5000)


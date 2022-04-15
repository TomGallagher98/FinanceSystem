import datetime

from flask import Flask, request, has_request_context

from flask_restful import Resource, Api
import sqlite3
import logging
from logging.config import dictConfig
from requests import put, get, post, delete, exceptions

app = Flask(__name__)
api = Api(app)

# Moved to Authentication Page
# def create_database():
#     # Will be run if the database is not detected
#     conn = sqlite3.connect("Finance_System.db")
#     cursorObject = conn.cursor()
#     cursorObject.execute("""CREATE TABLE Jobs(id integer PRIMARY KEY,
#                       user text,
#                       time timestamp,
#                       status text,
#                       daterange text,
#                       assets integer)""")
#
#     cursorObject.execute("""CREATE TABLE Results (id integer PRIMARY KEY,
#                           jobID integer,
#                           time timestamp,
#                           assets integer)""")


class MasterData(Resource):
    # Send user ID, token, job ID
    # First checks token/user is valid
    # Then returns job if valid
    def get(self):
        # Checks that the user can perform the job
        token = request.json['token']
        id = request.json['job_id']
        data = get('http://localhost:5000/check_token/api/' + token,
                   json={'user': 'Tom', 'job': 'Results'}).json()
        print(data)
        if data['message'] != 'Valid':
            app.logger.info({'message': 'Authorization Error'})
            return {'Error': 'Authorization Error: You do not have access to this resource'}
        else:
            # selects the job by id from sql database
            conn = sqlite3.connect('Finance_System.db', timeout=10)
            cursorObj = conn.cursor()
            cursorObj.execute(
                f'Select * FROM Results WHERE id = :i', {"i": id})
            results = cursorObj.fetchall()
            # business logic, access database return job results
            app.logger.info({'message': 'Results'})
            return 'Your results are in'
    ## Update Job
    def put(self):
        token = request.json['token']
        data = get('http://localhost:5000/check_token/api/' + token,
                   json={'user': 'Tom', 'job': 'Update'}).json()
        print(data)
        if data['message'] != 'Valid':
            app.logger.info({'message' : 'Authorization Error'})
            return {'Error': 'Authorization Error: You do not have access to this resource'}
        else:
            # business logic, get input from user, access database, update job table
            # Will change once I have a better idea how the update feature will be used
            app.logger.info({'message': 'Successfully updated job'})
            return 'Successfully updated job'

    # Create Job
    # Will also access the computation service when it is implemented
    def post(self):
        token = request.json['token']
        user = request.json['user']
        assets = request.json['assets']
        # Checks that the user is authorized
        data = get('http://localhost:5000/check_token/api/' + token,
                   json={'user': 'Tom', 'job': 'Batch'}).json()
        # Returns Authorization error if the user does not have permission to access the service
        if data['message'] != 'Valid':
            message = {'message': 'Authorization Error'}
            app.logger.info(message)
            return {'message': 'Authorization Error: You do not have access to this resource'}
        else:
            # Adds job to job table
            conn = sqlite3.connect('Finance_System.db', timeout=10)
            cursorObj = conn.cursor()
            cursorObj.execute(
                f'INSERT INTO Jobs VALUES(:id, :u, :t, :s, :d, :a)',
                {"id": 'id', "u": user, "t": datetime.datetime.now(), "s": 'Pending', "d": datetime.datetime.date(), "a": assets})
            conn.commit()
            # business logic, get input from user, access database and calculation service
            message = {'message': 'Job started'}
            app.logger.info(message)
            return {'message': message}



api.add_resource(MasterData, '/Master_Data/api/')

if __name__ == '__main__':

    logging.basicConfig(level=logging.INFO, filename='log/finance.log')
    logging.getLogger('werkzeug').setLevel(logging.DEBUG)
    app.run(debug=True,port=8080)

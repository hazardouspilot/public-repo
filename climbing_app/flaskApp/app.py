#cd C:\Users\harol\public-repo\climbing_app\flaskApp

import re
from flask import Flask, render_template, request, redirect, url_for, session
from Database_Class import BWDB
from datetime import datetime
from util import hash_pass, verify_pass
#from flask_mysqldb import MySQL # type: ignore
# import MySQLdb.cursors
# import MySQLdb.cursors, re #, hashlib

app = Flask(__name__)

app.secret_key = 'unguessable-key'

MY_HOST = "localhost"
MY_USER = "root"
MY_PASS = "ClimbingShoes"
DATABASE = "climbing_mysql"

db = BWDB(
    dbms="mysql", host=MY_HOST, user=MY_USER, 
    password=MY_PASS, database=DATABASE
)

@app.route('/', methods=['GET', 'POST'])
def home():
    # Output message if something goes wrong...
    msg = ''
    email = ''
    # Check if "username" and "password" POST requests exist (user submitted form)
    if request.method == 'POST':
        # Create variables for easy access
        email = request.form['email']
        password = request.form['password']
        
        query = f"SELECT Username, Pass FROM climbers WHERE Email = '{email}'"
        
        # details for matching climber
        climber_iterator = db.sql_query(query)
        climber = next(climber_iterator, None)
        
        # if there's a match
        if climber:
            #if password matches, update session details and go to main page
            if verify_pass(password,climber[1]):
                session['user'] = climber[0]
                session['loggedin'] = True
                return render_template('mainpage.html')
            #otherwise update error message
            else:
                msg = 'Wrong password'
                return render_template('home.html', msg=msg, email=email)
        #no match for email, update error message accordingly
        else:
            msg = 'No existing user with that email address'
    return render_template('home.html', msg=msg)

@app.route('/logout')
def logout():
# Remove session data, this will log the user out
   session.pop('loggedin', None)
   session.pop('user', None)
   # Redirect to login page
   return redirect(url_for('home'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    msg = ''
    email = ''
    if request.method == 'POST':
        #get form submissions
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']
        # Check if email is already registered
        query = 'SELECT * FROM climbers WHERE Email = %s'

        account_iterator = db.sql_query(query, (email,))
        account = next(account_iterator, None)

        if account:
            msg = 'Email already registered'
            return render_template('register.html', msg=msg, email=email)
        # Check if username is available
        query = 'SELECT * FROM climbers WHERE Username = %s'
        
        account_iterator = db.sql_query(query, (username,))
        account = next(account_iterator, None)

        if account:
            msg = 'Username taken'
            return render_template('register.html', msg=msg, email=email)
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username restricted to only characters and numbers'
            return render_template('register.html', msg=msg, email=email)
        else:
            # Hash the password
            password = hash_pass(password)
            # Ensure the password is a string (decode if it's in bytes)
            if isinstance(password, bytes):
                password = password.decode('utf-8')
            # Account doesn't exist, and the form data is valid, so insert the new account into the accounts table
            query = 'INSERT INTO climbers (Username, Pass, Email) VALUES (%s, %s, %s)'
            
            db.sql_do(query, (username, password, email))
            msg = 'You have been registered'
            return render_template('home.html', msg=msg)
    return render_template('register.html', msg=msg, email=email)

@app.route('/reset_password', methods=['GET', 'POST'])
def reset():
    #add post functionality to verify existing password and update pass in climbers table
    return render_template('reset_password.html')

@app.route('/mainpage', methods=['GET', 'POST'])
def mainpage():
    return render_template('mainpage.html', user=session['user'])

@app.route('/add_routes', methods=['GET', 'POST'])
def add_routes():

    if request.method == 'GET':
        query = 'SELECT CompanyName FROM companys'
        db.table = "companys"
        companies_avail = list(db.sql_query(query))
        # selections = ''
        # gyms_avail = []
        # locations_avail = []
        # grades_avail = []
        # colours_avail = []
        session['step'] = 'step1'
        step = session.get('step', 'step1')
        return render_template('add_routes.html', step=step,  
                           companies_avail=companies_avail)

    if request.method == 'POST':
        
        # Step 1: Handle initial form submission
        if 'number_of_routes' in request.form and 'company' in request.form:
            number_of_routes = request.form['number_of_routes']
            session['number_of_routes'] = request.form['number_of_routes']
            session['company'] = request.form['company']
            session['step'] = 'step2'
            selections = f"Adding {session['number_of_routes']} routes at {session['company']}"
            # get list of available gyms
            query = 'SELECT Suburb FROM gyms WHERE CompanyName = %s'
            db.table = "gyms"
            gyms_avail = list(db.sql_query(query, (session['company'],)))
            
            step = session.get('step', 'step1')
            return render_template('add_routes.html', step=step, selections=selections, 
                           gyms_avail=gyms_avail)
        
        # Step 2: Handle gym and climb type submission
        elif 'gym' in request.form and 'climb_type' in request.form:
            session['gym'] = request.form['gym']
            session['climb_type'] = request.form['climb_type']
            session['step'] = 'step3'
            session['gradeSystem'] = 'no companies under that name in the company table'
            # get the grade system
            query = "SELECT * FROM companys WHERE CompanyName = %s"
            db.table = "companys"
            result = list(db.sql_query(query, (session['company'],)))
            if session['climb_type'] == "boulder":
                if result:
                    session['gradeSystem'] = result[0][1]
            elif session['climb_type'] == "sport":
                if result:
                    session['gradeSystem'] = result[0][2]
            query = "SELECT Colour FROM colours WHERE CompanyName = %s"
            db.table = "colours"
            colours_avail = list(db.sql_query(query, (session['company'],)))
            # get lists of available locations and grades
            db.table = "locations"
            query = "SELECT Location FROM locations WHERE CompanyName = %s AND Suburb = %s AND Area = %s"
            locations_avail = list(db.sql_query(query, (session['company'], session['gym'], session['climb_type'],)))
            db.table = "grades"
            query = "SELECT Grade FROM grades WHERE GradingSystem = %s"
            grades_avail = list(db.sql_query(query, (session['gradeSystem'],)))
            selections = f"Adding {session['number_of_routes']} {str(session['climb_type']).lower()} routes at {session['company']} {session['gym']}"
        
            step = session.get('step', 'step1')
            return render_template('add_routes.html', step=step, selections=selections,  
                            locations_avail=locations_avail, grades_avail=grades_avail,
                            colours_avail=colours_avail)
            
            
        # Step 3: Handle routes submission
        elif 'location-0' in request.form:  # Assuming there will always be at least one route
            routes = []
            number_of_routes = int(session['number_of_routes'])
            for i in range(number_of_routes):
                route = {
                    'location': request.form[f'location-{i}'],
                    'grade': request.form[f'grade-{i}'],
                    'colour': request.form[f'colour-{i}']
                }
                route['nHolds'] = 0
                if session['climb_type'] == 'boulder':
                    route['nHolds'] = request.form[f'nHolds-{i}']
                routes.append(route)
            date = datetime.now().date()
            # Save to session or process data as needed
            db.table = 'routes'
            for i in range(int(number_of_routes)):
                query = ('INSERT INTO routes (CreationDate, CompanyName, Suburb, Location, GradingSystem, Grade, Type_column, Colour, Existing, NumberHolds) '
                         'VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)')
                db.sql_do(query, (date, session['company'], session['gym'], routes[i]['location'], session['gradeSystem'], routes[i]['grade'], session['climb_type'], routes[i]['colour'], 1, routes[i]['nHolds']))
            session['routes'] = routes
            session['step'] = 'success'
            return redirect(url_for('success'))
        
    # step = session.get('step', 'step1')
    # return render_template('add_routes.html', step=step, selections=selections, 
    #                        companies_avail=companies_avail, gyms_avail=gyms_avail, 
    #                        locations_avail=locations_avail, grades_avail=grades_avail,
    #                        colours_avail=colours_avail)


@app.route('/success')
def success():
    routes = session.get('routes', [])
    return f"Form submitted successfully with routes: {routes}"

@app.route('/add_attempt', methods=['GET', 'POST'])
def add_attempt():
    date = datetime.now().date()
    time = datetime.now().strftime('%H:%M:%S')
    #functionality to add 
    return render_template('add_attempt.html', user=session['user'])

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    #functionality to update profile, maybe reset password here?
    return render_template('profile.html', user=session['user'])

@app.route('/boulder_history', methods=['GET', 'POST'])
def boulder_history():
    #functionality to view boulder history + videos
    return render_template('boulder_history.html', user=session['user'])

@app.route('/sport_history', methods=['GET', 'POST'])
def sport_history():
    #functionality to view sport attempt history, sorted by various metrics
    return render_template('sport_history.html', user=session['user'])

@app.route('/browse', methods=['GET', 'POST'])
def browse():
    #functionality to view all user's bouldering videos
    return render_template('browse.html', user=session['user'])

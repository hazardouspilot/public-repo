#cd C:\Users\harol\public-repo\climbing_app\flaskApp

import re
from flask import Flask, render_template, request, redirect, url_for, session
from Azure_Database_Class import azureSQLdb
from datetime import datetime
from util import hash_pass, verify_pass

app = Flask(__name__)

app.secret_key = 'unguessable-key'

#configure database connection
MY_HOST = "climbing-database-server.database.windows.net,1433"
MY_USER = "CloudSAc013d50c@climbing-database-server"
MY_PASS = "z85nB22htMNj$yiP"
DATABASE = "climbing-database"

#create database from class in Azure_Database_Class.py
db = azureSQLdb(
    dbms="sqlserver", host=MY_HOST, user=MY_USER, 
    password=MY_PASS, database=DATABASE
)

#log in page
@app.route('/', methods=['GET', 'POST'])
def home():
    # Output message if something goes wrong...
    msg = False
    email = ''

    # Check if "username" and "password" POST requests exist (user submitted form)
    if request.method == 'POST':
        # Create variables for easy access
        email = request.form['email']
        password = request.form['password']
        

        query = f"SELECT Username, Pass FROM Climbers WHERE Email = '{email}'"
        
        # details for matching climber
        climber_iterator = db.sql_query(query)
        climber = next(climber_iterator, None)
        
        # if there's a match
        if climber:
            #if password matches, update session details and go to main page
            if verify_pass(password,climber[1]):
                session['user'] = climber[0]
                session['email'] = email
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
        query = 'SELECT * FROM Climbers WHERE Email = ?'

        account_iterator = db.sql_query(query, (email,))
        account = next(account_iterator, None)

        if account:
            msg = 'Email already registered'
            return render_template('register.html', msg=msg, email=email)
        # Check if username is available
        query = 'SELECT * FROM Climbers WHERE Username = ?'
        
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
            query = 'INSERT INTO Climbers (Username, Pass, Email) VALUES (?, ?, ?)'
            
            db.sql_do(query, (username, password, email))
            msg = 'You have been registered'
            return render_template('home.html', msg=msg)
    return render_template('register.html', msg=msg, email=email)

@app.route('/mainpage', methods=['GET', 'POST'])
def mainpage():
    return render_template('mainpage.html')

@app.route('/add_routes', methods=['GET', 'POST'])
def add_routes():
    if request.method == 'GET':
        selections = 'Add new climbing routes or boulder problems'
        query = 'SELECT CompanyName FROM Companys'
        db.table = "companys" #needed?
        companies_avail = list(db.sql_query(query))
        session['step'] = 'step1'
        step = session.get('step', 'step1')
        return render_template('add_routes.html', step=step,  
                           companies_avail=companies_avail, selections=selections)
    if request.method == 'POST':
        # Step 1: Handle initial form submission
        if 'number_of_routes' in request.form and 'company' in request.form:
            number_of_routes = request.form['number_of_routes']
            session['number_of_routes'] = request.form['number_of_routes']
            session['company'] = request.form['company']
            session['step'] = 'step2'
            selections = f"Adding {session['number_of_routes']} route/s at {session['company']}"
            # get list of available gyms
            query = 'SELECT Suburb FROM Gyms WHERE CompanyName = ?'
            db.table = "gyms" #needed?
            gyms_avail = list(db.sql_query(query, (session['company'],)))
            
            step = session.get('step', 'step1')
            return render_template('add_routes.html', step=step, selections=selections, 
                           gyms_avail=gyms_avail)
        
        # Step 2: Handle gym and climb type submission
        elif 'gym' in request.form and 'climb_type' in request.form:
            session['gym'] = request.form['gym']
            session['climb_type'] = request.form['climb_type']
            session['step'] = 'step3'
            # get the grade system
            query = "SELECT * FROM Companys WHERE CompanyName = ?"
            
            result = list(db.sql_query(query, (session['company'],)))
            print(result)
            print(session['climb_type'])
            if str(session['climb_type']).lower() == "boulder":
                if result:
                    session['gradeSystem'] = result[0][1]
            elif str(session['climb_type']).lower() == "sport":
                if result:
                    session['gradeSystem'] = result[0][2]
            
            query = "SELECT Colour FROM Colours WHERE CompanyName = ?"
            
            colours_avail = list(db.sql_query(query, (session['company'],)))
            # get lists of available locations and grades
            
            query = "SELECT Location FROM Locations WHERE CompanyName = ? AND Suburb = ?"
            locations_avail = list(db.sql_query(query, (session['company'], session['gym'],)))
            
            query = "SELECT Grade FROM Grades WHERE GradingSystem = ?"
            grades_avail = list(db.sql_query(query, (session['gradeSystem'],)))
            selections = f"Adding {session['number_of_routes']} {str(session['climb_type']).lower()} route/s at {session['company']} {session['gym']}"
        
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
            db.table = 'routes' #needed?
            for i in range(int(number_of_routes)):
                query = ('INSERT INTO routes (CreationDate, CompanyName, Suburb, Location, GradingSystem, Grade, Type_column, Colour, Existing, NumberHolds) '
                         'VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)')
                db.sql_do(query, (date, session['company'], session['gym'], routes[i]['location'], session['gradeSystem'], 
                                  routes[i]['grade'], session['climb_type'], routes[i]['colour'], 1, routes[i]['nHolds']))
            session['routes'] = routes
            msg = 'Route/s added successfully'
            return render_template('mainpage.html', msg=msg)
    return render_template('add_routes.html')

@app.route('/add_attempt', methods=['GET', 'POST'])
def add_attempt():
    if request.method == 'GET':
        selections = 'Add new attempt'
        query = 'SELECT CompanyName FROM Companys'
        
        companies_avail = list(db.sql_query(query))
        session['step'] = 'step1'
        step = session.get('step', 'step1')
        return render_template('add_attempt.html', step=step,  
                           companies_avail=companies_avail, selections=selections)
    
    if request.method == 'POST':
        # Step 1: Handle initial form submission
        if 'company' in request.form:
            session['company'] = request.form['company']
            session['step'] = 'step2'
            selections = f"Adding attempt at {session['company']}"
            # get list of available gyms
            query = 'SELECT Suburb FROM Gyms WHERE CompanyName = ?'
            
            gyms_avail = list(db.sql_query(query, (session['company'],)))
            step = session.get('step', 'step1')
            return render_template('add_attempt.html', step=step, selections=selections, 
                           gyms_avail=gyms_avail)
        # Step 2: Handle gym and climb type submission
        elif 'gym' in request.form and 'climb_type' in request.form:
            session['gym'] = request.form['gym']
            session['climb_type'] = request.form['climb_type']
            session['step'] = 'step3'
            selections = f"Adding {str(session['climb_type']).lower()} attempt at {session['company']} {session['gym']}"
            # get lists of available locations and grades
            
            query = "SELECT Location FROM Locations WHERE CompanyName = ? AND Suburb = ?"
            # locations_avail = list(db.sql_query(query, (session['company'], session['gym'])))
            locations_result = list(db.sql_query(query, (session['company'], session['gym'])))
            locations_avail = [location[0] for location in locations_result]
            session['locals'] = locations_avail
            step = session.get('step', 'step1')
            return render_template('add_attempt.html', step=step, selections=selections,  
                            locations_avail=locations_avail)
        # Step 3: Handle location submission
        elif 'location' in request.form or session['step'] == 'step4':
            try:
                session['location'] = request.form['location']
            except:
                print("add_attempt loaded at step 4 without location form input")
            session['step'] = 'step4'
            selections = f"Existing routes at location {session['location']}(please archive removed routes):"
            step = session.get('step', 'step1')
            # find routes at selected location and store details in list
            query = "SELECT RID, CreationDate, Grade, Colour, NumberHolds FROM Routes WHERE CompanyName = ? AND Suburb = ? AND Location = ? AND Existing = 1"
            routes = list(db.sql_query(query, (session['company'], session['gym'], session['location'],)))
            
            return render_template('add_attempt.html', step=step, selections=selections,  
                            routes=routes)
        # Step 4: Handle final attempt details submission and update database
        elif session['step'] == 'step5':
            attemptNo = request.form['attempt']
            result = request.form['result']
            rating = request.form['rating']
            notes = request.form['notes']
            if session['climb_type'] == 'sport':
                mode = request.form['mode']
            else:
                mode = ''

            # Handle video file upload
            video_data = None
            if 'video' in request.files:
                video = request.files['video']
                if video.filename != '':
                    # Read the file data
                    video_data = video.read()
            # Format date and time for SQL Server
            current_datetime = datetime.now()
            date = current_datetime.strftime('%Y-%m-%d')
            time = current_datetime.strftime('%H:%M:%S')

            #check for duplicate attempt entries
            query = ("SELECT * FROM Attempts WHERE Username = ? AND RID = ? AND Mode_column = ? AND AttemptNo = ?")
            duplicates = list(db.sql_query(query, (session['user'], session['RID'], mode, attemptNo, )))
            if len(duplicates) > 0:
                step = session.get('step', 'step1')
                selections = 'You have already logged an attempt with these details, if this is a new attempt, use a higher attempt number'
                query = "SELECT RID, CreationDate, Grade, Colour, NumberHolds FROM Routes WHERE CompanyName = ? AND Suburb = ? AND Location = ? AND Existing = 1"
                routes = list(db.sql_query(query, (session['company'], session['gym'], session['location'],)))
                return render_template('add_attempt.html', step=step, selections=selections,  
                            routes=routes)

            #add new attempt
            query = ("INSERT INTO Attempts (Username, RID, Mode_column, AttemptNo, Date_column, Time_column, Result, Rating, Notes, Video)"
                     "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)")
            db.sql_do(query, (session['user'], session['RID'], mode, attemptNo, date, time, result, rating, notes, video_data))
            #reload add attempt page using same company, gym and climb type
            session['step'] = 'step3'
            step = session.get('step', 'step1')
            selections = 'Attempt added successfully, ready to add another'

            #reset available locations
            locations_avail = session['locals']
            return render_template('add_attempt.html', step=step, selections=selections,  
                            locations_avail=locations_avail)

@app.route('/archiveRoute', methods=['POST'])
def archiveRoute():
    if request.method == 'POST':
        RID = request.form['RID']
        print(f"Route ID to be archived: {RID}")
        query = "UPDATE routes SET Existing = 0 WHERE RID = ?"
        db.sql_do(query, (RID,))
        selections = f"Existing routes at location {session['location']} (please archive removed routes):"
        session['step'] = 'step4'
        step = session.get('step', 'step1')
        query = "SELECT RID, CreationDate, Grade, Colour, NumberHolds FROM Routes WHERE CompanyName = ? AND Suburb = ? AND Location = ? AND Existing = 1"
        routes = list(db.sql_query(query, (session['company'], session['gym'], session['location'],)))
        return render_template('add_attempt.html', step=step, selections=selections, routes=routes)
    return render_template('mainpage.html')

@app.route('/selectRoute', methods=['GET', 'POST'])
def selectRoute():
    if request.method == 'POST':

        session['RID'] = request.form['RID']
        selections = "Route selected"
        session['step'] = 'step5'
        step = session.get('step', 'step1')
        print(f"Step updated to {step} by selectRoute function")
        return render_template('add_attempt.html', step=step, selections=selections)
    return render_template('mainpage.html')

@app.route('/reset_password', methods=['GET', 'POST'])
def reset():
    #add post functionality to verify existing password and update pass in climbers table
    return render_template('reset_password.html')

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
    query = "SELECT Video FROM Attempts"
    videos = db.sql_query(query)
    return render_template('browse.html', videos=videos)

@app.route('/add_locations', methods=['GET', 'POST'])
def add_locations():
    #functionality to add new locations for a specific company & gym
    return render_template('add_locations.html', user=session['user'])
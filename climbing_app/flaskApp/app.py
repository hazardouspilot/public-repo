from flask import Flask, render_template, request, redirect, url_for, session
from Database_Class import BWDB
from datetime import datetime
from util import hash_pass, verify_pass
from flask_mysqldb import MySQL # type: ignore
import MySQLdb.cursors
import MySQLdb.cursors, re #, hashlib

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

@app.route('/add_route', methods=['GET', 'POST'])
def add_route():
    #functionality to add new route
    return render_template('add_route.html', user=session['user'])

@app.route('/add_attempt', methods=['GET', 'POST'])
def add_attempt():
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

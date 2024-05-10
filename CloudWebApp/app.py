from flask import Flask
import boto3
from boto3.dynamodb.conditions import Key
from flask import render_template, request, redirect, url_for, flash, abort, jsonify
from werkzeug.utils import secure_filename
from jinja2 import Template
import requests

app = Flask(__name__)

app.secret_key = 'unguessable-key'
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
table1_name = 'login'
table2_name = 'subs'
table3_name = 'music'
bucket_url = 'https://s3997902-bucket-public.s3.amazonaws.com/'
API_ENDPOINT_REGO = 'https://kd99tgp34l.execute-api.us-east-1.amazonaws.com/Deployment/ass1_rego'
API_ENDPOINT_ADD = 'https://p6vx0b9ly1.execute-api.us-east-1.amazonaws.com/Deployment/ass1_add'
API_ENDPOINT_REMOVE = 'https://4eyi8czonc.execute-api.us-east-1.amazonaws.com/Deployment/ass1_remove'
active_user = 'blank'
active_email = ''

@app.route('/', methods=['GET', 'POST']) #
def home():
    #specify use of global variables
    global active_user
    global active_email
    #if user clicks log in
    if request.method == 'POST':
        #retireve table from aws
        table = dynamodb.Table(table1_name)
        #update global variables with user entered text
        active_email = request.form['email']
        active_password = request.form['password']
        #retrieve row from table with matching email, if it exists
        response = table.get_item(
            Key={
                'email': active_email
            }
        )
        #if the item exists and if the password matches
        if 'Item' in response:
            item = response['Item']
            if item['password'] == active_password:
                #set active user and go to mainpage
                active_user = item['user_name']
                return redirect(url_for('mainpage'))
            else:
                flash('Email or password is invalid', 'invalid_email_password')
                return render_template('home.html')
        else:
            flash('Email or password is invalid', 'invalid_email_password')
            return render_template('home.html')
    return render_template('home.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        #get form submissions
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']
        #compile for API submission
        payload = {
            'type': 'update', 
            'email': email,
            'username': username,
            'password': password
        }
        #smack the APIs butt and see how it likes it
        response = requests.post(API_ENDPOINT_REGO, json=payload)

        #didn't like it
        if 'statusCode' in response.json() and response.json()['statusCode'] == 409:
            flash('The email already exists', 'invalid_email')
            return render_template('register.html')
        #loved it
        elif 'statusCode' in response.json() and response.json()['statusCode'] == 200:
            flash("Registration successful, please log in", 'successful_rego')
            return redirect(url_for('home'))
        #not sure
        else:
            flash('Unexpected error', 'unexpected_status_code')
            return render_template('register.html')
    return render_template('register.html')

@app.route('/mainpage', methods=['GET', 'POST'])
def mainpage():
    global active_email
    #initiate song list
    list_songs = []
    #get table user subscriptions
    table = dynamodb.Table(table2_name)
    #extract rows associated with active user
    response = table.scan(FilterExpression=Key('user_email').eq(active_email))
    #check if the user had any subs before persisting
    if 'Items' in response:
        #for each row append a dictionary with key = 'title' and value = the value from the 'song_title' column
        for item in response['Items']:
            title = item.get('song_title')
            if title:
                list_songs.append({'title': title})
    
    #now get songs' other details from music table to add to dictionary
    table2 = dynamodb.Table(table3_name)
    for song in list_songs:
        response = table2.query(KeyConditionExpression=Key('title').eq(song['title']))
        song['artist'] = response['Items'][0]['artist']
        song['year'] = response['Items'][0]['year']
        #images have been downloaded into S3 bucket with names <song_title>_<song_year>.jpg
        #in the image URLs, spaces are replaced with +
        url_song_title = str(song['title']).replace(' ', '+')
        song['img_url'] = bucket_url + url_song_title + '_' + str(song['year']) + '.jpg'

    #initiate list of query results
    queried_songs = []
    if request.method == 'POST':
        #retrieve song table
        table3 = dynamodb.Table(table3_name)
        #retrieve search parameters
        query_title = request.form['title']
        query_year = request.form['year']
        query_artist = request.form['artist']
        response = table3.scan()

        for item in response['Items']:
            if query_title.lower() in item['title'].lower() and query_artist.lower() in item['artist'].lower() and str(query_year) in str(item['year']):
                queried_songs.append({'title': item['title']})

        if len(queried_songs) == 0:
            flash("No result is retrieved. Please query again.", 'no_query_results')
        else:
            #get songs' other details from music table to add to dictionary
            for song in queried_songs:
                response = table2.query(KeyConditionExpression=Key('title').eq(song['title']))
                song['artist'] = response['Items'][0]['artist']
                song['year'] = response['Items'][0]['year']
                #images have been downloaded into S3 bucket with names <song_title>_<song_year>.jpg
                #in the image URLs, spaces are replaced with +
                url_song_title = str(song['title']).replace(' ', '+')
                song['img_url'] = bucket_url + url_song_title + '_' + str(song['year']) + '.jpg'

    return render_template('mainpage.html', active_user=active_user, list_songs=list_songs, queried_songs=queried_songs)

@app.route('/remove_song', methods=['GET', 'POST'])
def removeSong():
    #get info for song to remove
    title = request.form['title']
    email = active_email
    #prep info for API
    payload = {
            'type': 'update', 
            'title': title,
            'email': email
        }
    #slap that API
    requests.post(API_ENDPOINT_REMOVE, json=payload)
    
    return redirect(url_for('mainpage'))

@app.route('/add_song', methods=['GET', 'POST'])
def addSong():
    #get info for song to add
    title = request.form['title']
    email = active_email
    #prep info for API
    payload = {
            'type': 'update', 
            'title': title,
            'email': email
        }
    #hit the API with the info
    requests.post(API_ENDPOINT_ADD, json=payload)

    return redirect(url_for('mainpage'))
from flask import Flask
import boto3
from boto3.dynamodb.conditions import Key
from flask import render_template, request, redirect, url_for, flash, abort, jsonify
from werkzeug.utils import secure_filename
from jinja2 import Template
# import json
# import os.path

app = Flask(__name__)

app.secret_key = 'unguessable-key'
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
table1_name = 'login'
table2_name = 'subs'
table3_name = 'music'
bucket_url = 'https://s3997902-bucket-public.s3.amazonaws.com/'

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
        #form submission
        table = dynamodb.Table(table1_name)
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']

        #retrieve row from table with matching email, if it exists
        response = table.get_item(
            Key={
                'email': email
            }
        )
        #if the email exists
        if 'Item' in response:
            flash('The email already exists', 'invalid_email')
            return render_template('register.html')
        else:
            #upload new user details to login table
            table.put_item(
                Item={
                    'email': email,
                    'user_name': username,
                    'password': password
                }
            )
            flash("Registration successful, please log in", 'successful_rego')
            #redirect back to login page
            return redirect(url_for('home'))
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
            if query_title in item['title'] and query_artist in item['artist'] and str(query_year) in str(item['year']):
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
    title = request.form['title']
    email = active_email
    table = dynamodb.Table(table2_name)
    table.delete_item(
                Key={
                    'song_title': title,
                    'user_email': email
                }
            )
    return redirect(url_for('mainpage'))

@app.route('/add_song', methods=['GET', 'POST'])
def addSong():
    title = request.form['title']
    email = active_email
    table = dynamodb.Table(table2_name)
    item = {
        'song_title': title,
        'user_email': email
    }
    response = table.put_item(Item=item)
    if response['ResponseMetadata']['HTTPStatusCode'] == 200:
        flash("Subscription added", 'successful_sub')
    else:
        #presumably, user already subscribed to this song
        flash("Subscription failed", 'unsuccessful_sub')
    return redirect(url_for('mainpage'))
# cd "C:\Users\harol\OneDrive\Desktop\RMIT\S3-02 Adv Prog for DS\Ass 2\Milestone 2"

from flask import Flask
from flask import render_template, request, flash, session
import numpy as np
import joblib
from gensim.models import KeyedVectors
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

#set number of matching jobs to show in job search
n_jobs = 20

#initialise a lemmatizer for search queries
lemmatizer = WordNetLemmatizer()

#initiate list of stop words for preprocessing descriptions of created jobs
stop_words = set(stopwords.words('english'))

#initialise our app
app = Flask(__name__)

#set a sectret key for the app
app.secret_key = 'something-unique-and-secret'

#initiate lists for job details
job_titles = []                 #Title
job_ids = []                    #Webindex
job_companies = []              #Company
job_descriptions = []           #Description, as per original files
job_descs_processed = []        #Description without punctuation, symbols, stop words, 
#                                most common words or single character words
job_categories = []             #Category

#open the cleaned text file
with open('jobs_clean.txt',"r",encoding = 'unicode_escape') as f:
    #for each line, save it to a list according to its index
    for i, line in enumerate(f):
        line = line.strip()
        if i % 6 == 0:
            job_titles.append(line)
        elif i % 6 == 1:
            job_ids.append(int(line))
        elif i % 6 == 2:
            job_companies.append(line)
        elif i % 6 == 3:
            job_descriptions.append(line)
        elif i % 6 == 4:
            job_descs_processed.append(line)
        else:
            job_categories.append(line)
    f.close()

#load pretrained word2vector model from file
pretrained_w2v_model = KeyedVectors.load('googleNews300_w2v.model')

#load pretrained SVM model from file
pretrained_svm_model = joblib.load('best_svm_model.pkl')

#home page
@app.route('/')
def home():
    return render_template('home.html')

#search page
@app.route('/search', methods=['GET', 'POST'])
def search():
    n_matching_jobs = 0
    if request.method == 'POST':
        #get search phrase from html form
        search_phrase = request.form['keyword'].lower()

        #tokenise it
        tokenized_phrase = word_tokenize(search_phrase)

        #lemmatize it
        lemmatized_phrase = [lemmatizer.lemmatize(token) for token in tokenized_phrase]

        #initialise list for matching jobs
        matching_jobs = []

        for i in range(len(job_ids)):
            title = job_titles[i].lower()
            desc = job_descs_processed[i]
            if all(word in title or word in desc for word in lemmatized_phrase):
                matching_jobs.append({
                    'id': job_ids[i],
                    'title': job_titles[i],
                    'category': job_categories[i],
                    'company': job_companies[i]
                })
        
        #save length of list
        n_matching_jobs = len(matching_jobs)

        #generate list of matching job ids to loop through in html file
        if n_matching_jobs == 0:
            flash('No jobs match that keyword', 'no_job_results')
        elif n_matching_jobs < n_jobs:
            return render_template('search.html', matching_jobs=matching_jobs, 
                                   n_matching_jobs=n_matching_jobs, n_jobs=n_jobs)
        else:
            return render_template('search.html', matching_jobs=matching_jobs[:n_jobs], 
                                   n_matching_jobs=n_matching_jobs, n_jobs=n_jobs)
    return render_template('search.html', n_matching_jobs=n_matching_jobs, n_jobs=n_jobs)

#create page
@app.route('/create', methods=['GET', 'POST'])
def create():
    if request.method == 'POST':
        if 'first_form_submitted' not in session:
            #actions for first form
            title = request.form['title']
            company = request.form['company']
            description = request.form['description']

            #vectorise model input data for category prediction
            input_data = (title + ' ' + description).lower().split()
            
            #valid keys are words in both the document and the model
            valid_keys = [term for term in input_data if term in pretrained_w2v_model]
            
            #compile matrix of word vectors from the model for each word in the document
            docvec = np.vstack([pretrained_w2v_model[term] for term in valid_keys])
            
            #sum columns to obtain document vector based on model
            docvec = np.sum(docvec, axis=0)
            
            #reshape document vector to 2D 
            docvec = docvec.reshape(1, -1)
            
            #use document vector based on unseen data with loaded model to predict label
            category_rec = pretrained_svm_model.predict(docvec)[0]

            #store the form data in the session
            session['title'] = title
            session['company'] = company
            session['description'] = description

            #mark the first form as submitted
            session['first_form_submitted'] = True

            #reload showing entered details and suggested category 
            return render_template('create.html', title=title, company=company, 
                                   description=description, category_rec=category_rec)

        else:
            #actions for second form
            category = request.form['category']

            #create new job id
            new_job_id = np.max(job_ids) + 1

            #preprocess (remove stop words) new description for future search functionality
            desc_tokens = word_tokenize(session['description'].lower())
            desc_preprocessed = " ".join([token for token in desc_tokens if token not in stop_words])

            #update job info lists
            job_titles.append(session['title'])
            job_ids.append(new_job_id)
            job_companies.append(session['company'])
            job_descriptions.append(session['description'])
            job_descs_processed.append(desc_preprocessed)
            job_categories.append(category)

            temp = session['company']
            #create flash message for when home page is loaded
            flash(f'New job listing for job at {temp} created successfully', 
                  'listing_created')

            # Clear the session data
            session.pop('title', None)
            session.pop('company', None)
            session.pop('description', None)
            session.pop('first_form_submitted', None)

            #load home page with flash message
            return render_template('home.html')
        
    #incase user submits first form but not second and reloads the create page
    session.pop('first_form_submitted', None)

    return render_template('create.html')

@app.route('/listing/<job_id>')
def listings(job_id):
    #find index of job matching the job_id from the selected job in the search results
    for i, job in enumerate(job_ids):
        if job == int(job_id):
            #save the details of the matching job and exit the for loop
            company_listing = job_companies[i]
            title = job_titles[i]
            category = job_categories[i]
            description = job_descriptions[i]
            break
    #render the listing page populated with the matching job details
    return render_template('listing.html', job_id=job_id, 
                           company=company_listing, title=title, 
                           category=category, description=description)
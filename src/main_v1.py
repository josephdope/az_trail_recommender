from hiking_data_v1 import DataGrabber, DetailsShaper, ReviewsShaper, DatabaseExport
from trail_recommender_v1 import ContentBased, CollabFilter
import psycopg2
import pandas.io.sql as sqlio
from selenium.webdriver.firefox.options import Options
from bs4 import BeautifulSoup
import re
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.action_chains import ActionChains
import time
import psycopg2
from sqlalchemy import create_engine
from collections import defaultdict
import re
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import StandardScaler
import pickle
import matplotlib.pyplot as plt


#GRAB ALL STATES FROM THE WORLD WIDE WEB
options = Options()
options.set_headless(True)
firefox_profile = webdriver.FirefoxProfile()
firefox_profile.set_preference("browser.privatebrowsing.autostart", True)
browser = webdriver.Firefox(options = options, firefox_profile = firefox_profile, executable_path='/usr/local/bin/geckodriver')
url = 'https://alphabetizer.flap.tv/lists/list-of-states-in-alphabetical-order.php'
browser.get(url)
page_content = BeautifulSoup(browser.page_source, 'html.parser')
scrape_results = page_content.findAll('li')
states = []
for res in scrape_results:
    states.append(res.text.replace(' ', '-'))
states.append('washington-dc')


##THIS IS FOR DATA IMPORT AND SQL EXPORT, IT DOES NOT NEED TO BE RUN AGAIN
exporter = DatabaseExport('az_trail_recommender')
grabber = DataGrabber()
grabber.grab_name_and_links(['alabama'])
links_1 = grabber.links_table
grabber.grab_details(links_1)

conn = psycopg2.connect("dbname='az_trail_recommender' user='josephdoperalski' host='localhost'")
cur = conn.cursor()
query_links = '''SELECT * FROM links'''
query_details = '''SELECT * FROM trail_details'''
query_reviews = '''SELECT * FROM trail_reviews'''
links = sqlio.read_sql_query(query_links, conn)
details = sqlio.read_sql_query(query_details, conn)
reviews = sqlio.read_sql_query(query_reviews, conn)
links.drop('index', axis = 1, inplace = True)
details.drop('index', axis = 1, inplace = True)
reviews.drop('index', axis = 1, inplace = True)

#Content-based data manipulation
details_shaper = DetailsShaper(details)
details_shaper.adjust_columns()
details_shaper.fix_column_data()
details_shaper.tfidf()
details_shaper.transform()
content_df = details_shaper.transformed_df

###CSV Export for Tableau
#details_shaper.proper_df.iloc[:, :59].to_csv('../../Tableau/tableau_df.csv')


#Collab-filtering data manipulation
reviews_shaper = ReviewsShaper(reviews)
reviews_shaper.fix_column_data()
reviews_shaper.user2user()
reviews_df = reviews_shaper.reviews_df
collab_df = reviews_shaper.user2user_df
user_ratings_count = collab_df.groupby('user', as_index=False).agg({'rating':'count'})
trail_ratings_count = collab_df.groupby('trail_id', as_index=False).agg({'rating':'count'})
active_users_trails = collab_df[(collab_df['user'].isin(user_ratings_count[user_ratings_count['rating'] >=10]['user'])) & (collab_df['trail_id'].isin(trail_ratings_count[trail_ratings_count['rating'] >= 20]['trail_id']))]

#Pivoted dataframe
pivot_collab_df = active_users_trails.groupby(['user', 'trail_id'], as_index = False).agg({'rating':'mean'}).pivot('user', 'trail_id', 'rating')
pivot_collab_df.fillna(0, inplace = True)
u, s, vh = np.linalg.svd(pivot_collab_df)
eigenvalues = s**2
eigen_cumsum = np.cumsum(eigenvalues)
eigen_cumsum[1000]/sum(eigenvalues)
features = len(eigen_cumsum[eigen_cumsum/sum(eigenvalues)<.9])
    


###TRAINING CONTENT BASED MODEL

content_based = ContentBased(content_df)
cosine_mat = content_based.create_cosine_mat()
content_results = content_based.recommend("Humphrey's Peak", cosine_mat)
content_results = links.merge(pd.DataFrame(content_results), on = 'trail_id')[['trail_id', 'trail']]



###TRAINING COLLABORATIVE FILTERING MODEL

collab_based = CollabFilter(active_users_trails)
##Finding best parameters
##score, params = collab_based.best_params()
##Fitting the model
collab_based.fit(n_fact = 11, n_epo = 50, lr_a = .003)
####Making recommendations
collab_based.recommend('amie-kimura')





##ReviewGenerator
#
#training = reviews[reviews['body'] != ''].sample(frac = .1)
##
#X, y, max_len, total_words = data_prep(training)
##
#model = fit(X, y, max_len, total_words)
##
#result = generate('yup', 20, max_len, model)



##Pickling stuff
#with open('collab_fit', 'wb') as fit_collab:
#    pickle.dump(collab_based, fit_collab)
#    
#with open('cosine_matrix', 'wb') as cos_mat:
#    pickle.dump(cosine_mat, cos_mat)
#    
#with open('transformed_details_df', 'wb') as trans_mat:
#    pickle.dump(content_df, trans_mat)
#    
#with open('details_df', 'wb') as dets_mat:
#    pickle.dump(details_shaper.proper_df, dets_mat)
#
#with open('collab_df', 'wb') as col_df:
#    pickle.dump(active_users_trails, col_df)
##
#




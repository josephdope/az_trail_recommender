from hiking_actual import DataGrabber, DataShaper
import psycopg2
import pandas.io.sql as sqlio
from selenium.webdriver.firefox.options import Options
from bs4 import BeautifulSoup
import re
import pandas as pd
import numpy as np
import requests
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


##### 12/10/18 #####

conn = psycopg2.connect("dbname='az_trail_recommender' user='josephdoperalski' host='localhost'")
cur = conn.cursor()
query = 'SELECT * FROM links'
data = sqlio.read_sql_query(query, conn)
data.set_index('trail_id', inplace = True)

#engine = create_engine('postgresql://josephdoperalski@localhost:5432/az_trail_recommender')
#P.to_sql('trail_info', engine)

#details = DataGrabber(url = None)
#
#details.links_table = data
#
#details.grab_details()
#
#X = details.details_table


#options = Options()
#options.set_headless(True)
#firefox_profile = webdriver.FirefoxProfile()
#firefox_profile.set_preference("browser.privatebrowsing.autostart", True)
#browser = webdriver.Firefox(options = options, firefox_profile = firefox_profile, executable_path='/usr/local/bin/geckodriver')




##### 12/11/19 #####


query2 = 'SELECT * FROM trail_info'
data2 = sqlio.read_sql_query(query2, conn)
data2.drop('index', axis = 1, inplace = True)
data2.set_index('trail_id', inplace = True)

shaper = DataShaper(data2)
shaper.adjust_columns()
shaper.fix_column_data()
shaper.tfidf()
proper_df = shaper.proper_df

scaler = StandardScaler()
transformed_df = scaler.fit_transform(proper_df.iloc[:,0:8].drop('trail_name', axis = 1))
transformed_df = pd.DataFrame(transformed_df)
transformed_df = pd.concat((data2['trail_name'], transformed_df, proper_df.iloc[:, 8:]), axis = 1)

proper_df.iloc[:,0:7].to_csv('data/no_tfidf_df.csv')
proper_df.to_csv('data/full_df.csv')


whatever = proper_df.iloc[:, 510]

def content_recommender(trail, sim_mat, df, indices):
    idx = indices[trail]
    sim_scores = list(enumerate(sim_mat[idx]))
    sim_scores = sorted(sim_scores, key = lambda x: x[1], reverse = True)
    sim_scores = sim_scores[1:11]
    trail_indices = [i[0] for i in sim_scores]
    return df['trail_name'].iloc[trail_indices]

indices = pd.Series(data2.index, index = data2['trail_name']).drop_duplicates()

cosine_sim = cosine_similarity(proper_df.drop('trail_name', axis = 1), proper_df.drop('trail_name', axis = 1))
content_recommender('Piestewa Peak Summit Trail #300', cosine_sim, transformed_df, indices)




indices.index



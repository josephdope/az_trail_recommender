from hiking_data_v02 import DataGrabber, DataShaper, DatabaseExport
from trail_recommender_v02 import Trail_Recommender
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
import pickle


###### 12/10/18 #####
#
conn = psycopg2.connect("dbname='az_trail_recommender' user='josephdoperalski' host='localhost'")
cur = conn.cursor()
query = 'SELECT * FROM links'
data = sqlio.read_sql_query(query, conn)


#
#
#dupes = data[data.duplicated(subset = 'trail', keep = False)]
#
#dupes.drop(1000, inplace = True)
#
#updated_names = ['Cathedral Rock Trail - Sedona', 'West Fork Trail - Sedona', 'Black Mountain Trail - Cave Creek', 'North Mountain National Trail long - Phoenix', 'Sunset Trail - Flagstaff', "Jacob's Crosscut Trail - Apache Junction", 'Wild Burro Trail - Marana', 'Black Rock Loop Trail - Waddell', 'Black Canyon Trail - Rock Springs', 'North Mountain National Trail - Phoenix', 'Black Rock Loop Trail - Tucson' , 'Wild Burro Trail - Peoria', "Jacob's Crosscut Trail long - Apache Junction", 'Sunset Trail - Tucson', 'Black Canyon Trail - Cottonwood', 'Black Mountain Trail - Henderson, NV', 'Cathedral Rock Trail - Las Vegas, NV', 'West Fork Trail - Palm Springs, CA', 'Cerro Grande Trail - Jemez Springs, NM']
#
#data.loc[dupes.index, 'trail'] = np.array(updated_names)
##data.set_index('trail_id', inplace = True)
#
#conn.close()
#cur.close()
#
#engine = create_engine('postgresql://josephdoperalski@localhost:5432/az_trail_recommender')
##P.to_sql('trail_info', engine)
#
#details = DataGrabber(url = None)
#
#details.links_table = data
#
#details.grab_details()
#
#X = details.details_table
#X.loc[dupes.index, 'trail_name'] = np.array(updated_names)
#X.drop('trail', axis = 1, inplace = True)
#exporter = DatabaseExport('az_trail_recommender')
#exporter.database_pandas(X, 'trail_info')
#
#
##options = Options()
##options.set_headless(True)
##firefox_profile = webdriver.FirefoxProfile()
##firefox_profile.set_preference("browser.privatebrowsing.autostart", True)
##browser = webdriver.Firefox(options = options, firefox_profile = firefox_profile, executable_path='/usr/local/bin/geckodriver')
#
#
#
#
###### 12/11/19 #####
#
#
query2 = 'SELECT * FROM trail_info'
data2 = sqlio.read_sql_query(query2, conn)
data2.drop('index', axis = 1, inplace = True)
#data2.set_index('trail_id', inplace = True)
#
#
#
#shaper = DataShaper(data2)
#shaper.adjust_columns()
#tags = shaper.fix_column_data()
#shaper.tfidf()
#shaper.transform()
#proper_df = shaper.proper_df
#trans_df = shaper.transformed_df

#
#
#
#
#proper_df = shaper.proper_df
#
#len(shaper.proper_df.columns)
#
#scaler = StandardScaler()
#transformed_df = scaler.fit_transform(proper_df.iloc[:,:9].drop(['trail_name','difficulty'], axis = 1))
#transformed_df = pd.DataFrame(transformed_df)
#transformed_df = pd.concat((data2['trail_name'], self.proper_df['difficulty'], transformed_df, proper_df.iloc[:,8:]), axis = 1)

##proper_df.iloc[:,0:7].to_csv('data/no_tfidf_df.csv')
##proper_df.to_csv('data/full_df.csv')
#
#
##whatever = proper_df.iloc[:, 510]
#
#def content_recommender(trail, sim_mat, df, indices):
#    idx = indices[trail]
#    sim_scores = list(enumerate(sim_mat[idx]))
#    sim_scores = sorted(sim_scores, key = lambda x: x[1], reverse = True)
#    sim_scores = sim_scores[1:11]
#    trail_indices = [i[0] for i in sim_scores]
#    return df['trail_name'].iloc[trail_indices]
#
#indices = pd.Series(data2.index, index = data2['trail_name']).drop_duplicates()
#
#cosine_sim = cosine_similarity(proper_df.drop('trail_name', axis = 1), proper_df.drop('trail_name', axis = 1))
#content_recommender('Piestewa Peak Summit Trail #300', cosine_sim, transformed_df, indices)
#                    
#                    
#content_recommender('Little Horse Trail', cosine_sim, transformed_df, indices)
#
#max_dist = proper_df[proper_df['dist'] == max(proper_df['dist'])]
#
#indices.index
#
###### 12/12/19 #####
#
#options = Options()
#options.set_headless(True)
#firefox_profile = webdriver.FirefoxProfile()
#firefox_profile.set_preference("browser.privatebrowsing.autostart", True)
#browser = webdriver.Firefox(options = options, firefox_profile = firefox_profile, executable_path='/usr/local/bin/geckodriver')
#url = 'https://www.alltrails.com/trail/us/arizona/piestewa-peak-summit-trail-300'
#browser.get(url)
#page_content = BeautifulSoup(browser.page_source, 'html.parser')
#
#lat = page_content.findAll('meta', attrs = {'itemprop':'latitude'})
#float(lat[0].attrs['content'])

shaper = DataShaper(data2)
shaper.adjust_columns()
tags = shaper.fix_column_data()
shaper.tfidf()
shaper.transform()
proper_df = shaper.proper_df
trans_df = shaper.transformed_df

#trans_df.loc[trans_df['trail_id'] == 6, 'trail_name'] = 'West Fork Trail - Sedona'
#
#trans_df[trans_df['trail_id'] == 6]
recommender = Trail_Recommender(trans_df)

cosine_mat = recommender.cosine_mat

filter_t = [x for x in trans_df['trail_name'] if 'Flatiron' in x]


trail = np.random.choice(trans_df['trail_name'], size = 1, replace = True)[0]
trail = "Humphrey's Peak"
print(trail)

result_trails = recommender.recommend(trail)
print(result_trails)
proper_df[proper_df['trail_id']==600]['trail_name']

new = pd.DataFrame(cosine_mat, index = trans_df.index, columns = trans_df.index)[100]

results = proper_df.loc[proper_df['trail_id'].isin(result_trails), ['trail_name', 'dist']]

results.join(new)

results.rename(columns = {results.columns[-1]: 'sim'}, inp)

results.sort_values(by = ['sim'], ascending = False)

#proper_df.iloc[:, 0:61].to_csv('../data/tableau_df.csv')

#print(list(dupes['trail']))

cosine_mat[results.index, proper_df[proper_df['trail_name'] == trail].index]

#with open('cosine_matrix', 'wb') as cm:
#    pickle.dump(new, cm)

#with open('transformed_df', 'wb') as tdf:
#    pickle.dump(trans_df, tdf)
#    
#with open('feature_df', 'wb') as fdf:
#    pickle.dump(proper_df, fdf)


##### 12/17/2018 #####

#SCRAPING REVIEWS DATA






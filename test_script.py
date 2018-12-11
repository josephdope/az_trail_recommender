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

query2 = 'SELECT * FROM trail_info'
data2 = sqlio.read_sql_query(query2, conn)
data2.drop('index', axis = 1, inplace = True)
data2.set_index('trail_id', inplace = True)



#options = Options()
#options.set_headless(True)
#firefox_profile = webdriver.FirefoxProfile()
#firefox_profile.set_preference("browser.privatebrowsing.autostart", True)
#browser = webdriver.Firefox(options = options, firefox_profile = firefox_profile, executable_path='/usr/local/bin/geckodriver')


shaper = DataShaper(data2)
shaper.adjust_columns()
shaper.fix_column_data()
shaper.tfidf()
proper_df = shaper.proper_df









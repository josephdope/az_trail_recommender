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
data.set_index('index', inplace = True)

engine = create_engine('postgresql://josephdoperalski@localhost:5432/az_trail_recommender')
P.to_sql('trail_info', engine)

details = DataGrabber(url = None)

details.links_table = data

details.grab_details()

X = details.details_table

options = Options()
options.set_headless(True)
firefox_profile = webdriver.FirefoxProfile()
firefox_profile.set_preference("browser.privatebrowsing.autostart", True)
browser = webdriver.Firefox(options = options, firefox_profile = firefox_profile, executable_path='/usr/local/bin/geckodriver')


shaper = DataShaper(X)

shaper.adjust_columns()

P = shaper.proper_df

shaper.fix_column_data()

proper_df = shaper.proper_df

test = float(re.findall(r"[-+]?\d*\.\d+|\d+", shaper.proper_df['dist'].iloc[1])[0])* 0.621371


proper_df['dist'].apply(lambda x: float(re.findall(r"[-+]?\d*\.\d+|\d+", x)[0] * 0.621371 if 'mile' not in x else float(re.findall(r"[-+]?\d*\.\d+|\d+", x)[0])))



deviate = [x for x in proper_df['elev'] if 'feet' not in x]




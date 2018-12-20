from hiking_data_v04 import DataGrabber, DataShaper, DatabaseExport
from trail_recommender_v04 import Trail_Recommender
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



exporter = DatabaseExport('az_trail_recommender')
if len(grabber.details_table) < 0:
    grabber = DataGrabber()
    grabber.grab_name_and_links()
    links = grabber.links_table    
    exporter.database_pandas(grabber.links_table, 'links')    
    trail_dict, review_dict = grabber.grab_details()

else:
    conn = psycopg2.connect


import pandas as pd
import numpy as np
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import StandardScaler
from nltk.tokenize import RegexpTokenizer
import time
import psycopg2
import pandas.io.sql as sqlio
from sqlalchemy import create_engine
from collections import defaultdict
import re
import math
import sys



def my_tokenizer(doc):
    tokenizer = RegexpTokenizer(r'\w+')
    article_tokens = tokenizer.tokenize(doc.lower())
    return article_tokens


def trail_details(t, page_content):
    details = page_content.findAll('div', attrs = {'class':'detail-data'})
    trail_info = []
    trail_info.append(t[1][0])
    trail_info.append(t[1][1])
    for p in details:
        trail_info.append(p.text)
    try:
        trail_info.append(page_content.findAll('div', attrs = {'id':'difficulty-and-rating'})[0].find('span')[0].text)
    except:
        trail_info.append('')
    try:
        trail_info.append(page_content.findAll('span' , attrs = {'class':'number'})[0].text)
    except:
        trail_info.append(0)
    lat = page_content.findAll('meta', attrs = {'itemprop':'latitude'})
    trail_info.append(float(lat[0].attrs['content']))
    long = page_content.findAll('meta', attrs = {'itemprop':'longitude'})
    trail_info.append(float(long[0].attrs['content']))
    try:
        tags_results = page_content.findAll('span', attrs = {'class':'big rounded active'})
        tags = []
        for tag in tags_results:
            tags.append(tag.text)
        tags = ','.join(tags)
        trail_info.append(tags)
    except:
        trail_info.append('')
    try:
        trail_info.append(page_content.findAll('section', attrs = {'id':'trail-top-overview-text'})[0].find('p').text)
    except:
        trail_info.append('')
    try:
        trail_info.append(page_content.findAll('div', attrs = {'id':'trail-detail-item'})[0].find('p').text)
    except:
        trail_info.append('')
    time.sleep(.5)
    print(trail_info)
    return trail_info


def trail_reviews(t, page_content):
    review_num = 0               
    reviews = page_content.findAll('div', attrs = {'itemprop':'review'})
    review_dict = defaultdict(list)         
    for i in reviews:
        review_id = str(t[1][0])+'_'+str(review_num) 
        review_list = []
        review_list.append(review_id)
        review_list.append(t[1][0])
        review_list.append(t[1][1])
        try:
            review_list.append(i.find(class_ = 'feed-user-content rounded').find(class_ = "width-for-stars-holder").find(class_ = 'link').attrs['href'])
        except:
            review_list.append('')
            
        try:
            review_list.append(i.find(itemprop = 'reviewRating').find(itemprop = 'ratingValue').attrs['content'])
        except:
            review_list.append('')
            
        try:                
            review_list.append(i.find(itemprop = 'reviewBody').text)
        except:
            review_list.append('')
        review_dict[review_id] = review_list
        review_num += 1
    return review_dict
                        


class DataGrabber():
    
    def __init__(self, browser = 'Firefox'):
        self.browser = browser
        self.links_table = pd.DataFrame()
        self.details_table = pd.DataFrame()
        self.reviews_table = pd.DataFrame()


    def grab_name_and_links(self, states = ['arizona']):
        for state in states:
            url = 'https://www.alltrails.com/us/'+state.lower()
            self.browser.get(url)
            time.sleep(3)
            page_content = BeautifulSoup(self.browser.page_source, 'html.parser')
            num_trails = int(re.sub("[^\d\.]", '', page_content.findAll('h3', attrs = {'class' : "top-trails"})[0].text))
            load_count = 0        
            elem = self.browser.find_element_by_css_selector('div.load-more:nth-child(3)')                
            self.browser.execute_script("arguments[0].scrollIntoView();", elem)
            time.sleep(.5)
            elem.click()
            trail_num = 0
            while load_count <= math.ceil(num_trails/24):
                try:
                    self.browser.execute_script("arguments[0].scrollIntoView();", elem)
                    time.sleep(.5)
                    elem.click()
                    time.sleep(0.5)
                    load_count += 1
                except:
                    break
            page_content_reload = BeautifulSoup(self.browser.page_source, 'html.parser')
            trail_cards = page_content_reload.findAll('div', attrs = {'class':'trail-result-card'})
#            trail_ids = []
#            names = []
#            location = []
#            links = []
            for i in trail_cards:
                trail_id = str(state)+str(trail_num)
                name = i.find(class_ = "name xlate-none short").attrs['title']
                link = 'alltrails.com'+i.attrs['itemid']
                area = i.findAll('span', attrs = {'class' : 'location-label'})[0].find('a').text
                trail_num += 1
                row = pd.Series([trail_id, name, state, area, link])
                print(row)
                self.links_table = self.links_table.append(row, ignore_index = True)
            print(self.links_table)
        self.links_table.columns = ['trail_id', 'trail', 'state', 'area', 'link']
        exporter = DatabaseExport('az_trail_recommender')
        exporter.database_pandas(self.links_table, 'links')
            
        
        
    def grab_details(self, df):
        exporter = DatabaseExport('az_trail_recommender')
        trail_dict = defaultdict(list)
        review_dict = defaultdict(list)
        trail_count = 0
        for t in df.iterrows():
            print(trail_count)
            trail_count += 1
            if (sys.getsizeof(trail_dict) + sys.getsizeof(review_dict)) > 2147483648:
                self.details_table = pd.DataFrame.from_dict(trail_dict, orient = 'index', columns = ['trail_id', 'trail_name', 'dist', 'elev', 'type', 'difficulty', 'num_completed','latitude', 'longitude' ,'tags', 'overview', 'full_desc'])
                self.reviews_table = pd.DataFrame.from_dict(review_dict, orient = 'index', columns = ['review_id', 'trail_id', 'trail_name', 'user', 'rating', 'body'])
                exporter.database_pandas(self.reviews_table, 'trail_reviews')                
                exporter.database_pandas(self.details_table, 'trail_details')
                self.reviews_table = pd.DataFrame()
                self.details_table = pd.DataFrame()
                trail_dict = defaultdict(list)
                review_dict = defaultdict(list)
            url = 'https://www.'+t[1][4]
            self.browser.get(url)
            page_content = BeautifulSoup(self.browser.page_source, 'html.parser')
            try:
                elem = self.browser.find_element_by_css_selector('div.feed-item:nth-child(31)')
                total_reviews = int(re.sub("[^\d\.]", '', page_content.findAll('a', attrs = {'name' : "Reviews"})[0].text))
                more_reviews = True
                load_count = 0
                while more_reviews == True and load_count < math.ceil(total_reviews/30):
                    try:                               
                        self.browser.execute_script("arguments[0].scrollIntoView();", elem)
                        elem.click()
                        time.sleep(2)
                        load_count += 1
                    except:
                        more_reviews = False
                print('loading reviews for ' + t[1][1])
            except:
                continue
            page_content_reload = BeautifulSoup(self.browser.page_source, 'html.parser')
            trail_dict[t[1][0]] = trail_details(t, page_content_reload)
            review_dict = {**review_dict, **trail_reviews(t, page_content_reload)}
        self.details_table = pd.DataFrame.from_dict(trail_dict, orient = 'index', columns = ['trail_id', 'trail_name', 'dist', 'elev', 'type', 'difficulty', 'num_completed','latitude', 'longitude' ,'tags', 'overview', 'full_desc'])
        self.reviews_table = pd.DataFrame.from_dict(review_dict, orient = 'index', columns = ['review_id', 'trail_id', 'trail_name', 'user', 'rating', 'body'])
        exporter.database_pandas(self.reviews_table, 'trail_reviews')                
        exporter.database_pandas(self.details_table, 'trail_details')       
                
    @property
    def browser(self):
        return self._browser
    
    @browser.setter
    def browser(self, value):
        if value == 'Firefox':
            options = Options()
            options.set_headless(True)
            firefox_profile = webdriver.FirefoxProfile()
            firefox_profile.set_preference("browser.privatebrowsing.autostart", True)
            self._browser = webdriver.Firefox(options = options, firefox_profile = firefox_profile, executable_path='/usr/local/bin/geckodriver')
        else:
            chrome_options = webdriver.ChromeOptions()
            chrome_options.add_argument("--incognito")
            chrome_options.add_argument("--headless")
            self._browser = webdriver.Chrome(chrome_options = chrome_options, executable_path='/usr/local/bin/chromedriver')       
            
    
class DetailsShaper():
    
    def __init__(self, raw_dataframe):
        self.raw = raw_dataframe
        self.proper_df = pd.DataFrame()
        self.transformed_df = pd.DataFrame()
        
    def adjust_columns(self):
        self.proper_df = self.raw.copy().iloc[:,0:-3]
        self.proper_df.loc[:,'text'] = self.raw.iloc[:,-2] + self.raw.iloc[:,-1]
        
    def fix_column_data(self):
        self.proper_df['dist'] = self.proper_df['dist'].apply(lambda x: float(re.findall(r"[-+]?\d*\.\d+|\d+", x)[0]) * 0.621371 if 'mile' not in x else float(re.findall(r"[-+]?\d*\.\d+|\d+", x)[0]))
        self.proper_df['elev'] = self.proper_df['elev'].apply(lambda x: float(re.sub("[^\d\.]", '',  x)) * 3.28084 if 'feet' not in x else float(re.sub('[^\d\.]','', x)))
        self.proper_df['num_completed'] = self.proper_df['num_completed'].apply(lambda x: float(re.sub("[^\d\.]", '',  x)))
        self.proper_df = pd.get_dummies(self.proper_df, columns = ['type'], drop_first = True)
        self.proper_df['difficulty'] = self.proper_df['difficulty'].apply(lambda x: 1 if x == 'EASY' else (2 if x == 'MODERATE' else 3))
        tags_set = set()
        [[tags_set.add(t) for t in x.split(',')] for x in self.raw['tags']]
        tags_df = pd.DataFrame(np.zeros((self.proper_df.shape[0], len(tags_set))), columns = tags_set, index = self.proper_df.index)
        for idx, row in self.raw['tags'].iteritems():
            for tag in row.split(','):
                tags_df.loc[idx, tag] = 1
        self.proper_df = pd.concat((self.proper_df, tags_df), axis = 1)
            
    def tfidf(self, tokenizer = my_tokenizer):
        vect = TfidfVectorizer(tokenizer = tokenizer, stop_words = 'english', ngram_range = (1,2), min_df = .05)
        tfidf_init = vect.fit_transform(self.proper_df['text'])
        tfidf_df = pd.DataFrame(tfidf_init.toarray(), columns = vect.get_feature_names(), index = self.proper_df.index)
        self.proper_df = pd.concat((self.proper_df.drop(['text'], axis = 1), tfidf_df), axis = 1)
        
    def transform(self):        
        scaler = StandardScaler()
        trans_df = scaler.fit_transform(self.proper_df.iloc[:,:8].drop(['trail_name','difficulty', 'trail_id'], axis = 1))
        trans_df = pd.DataFrame(trans_df)
        self.transformed_df = pd.concat((self.proper_df[['trail_id', 'trail_name']], trans_df, self.proper_df['difficulty'], self.proper_df.iloc[:,8:]), axis = 1)
        self.transformed_df.loc[:,0] = self.transformed_df.loc[:,0]*40
        self.transformed_df.loc[:,1] = self.transformed_df.loc[:,1]*20
        self.transformed_df.columns = ['trail_id', 'trail_name', 'dist', 'elev', 'num_completed', 'latitude', 'longitude','difficulty'] + list(self.proper_df.iloc[:, 8:].columns)
        
class ReviewsShaper():
    
    def __init__(self, raw_dataframe):
        self.raw_dataframe = raw_dataframe.copy()
        self.reviews_df = pd.DataFrame()
        self.user2user_df = pd.DataFrame()
      
    def fix_column_data(self):
        self.reviews_df = self.raw_dataframe.copy()
        self.reviews_df['user'] = self.reviews_df['user'].map(lambda x: re.sub('/members/', '', x))
        self.reviews_df.drop('trail_name', inplace = True, axis = 1)
        self.reviews_df['rating'] = self.reviews_df['rating'].astype(np.int_)
        
    def user2user(self):
        self.user2user_df = self.reviews_df
        self.user2user_df.drop(['review_id', 'body'], axis = 1, inplace = True)
        self.user2user_df.replace('', np.nan, inplace = True)
        self.user2user_df.dropna(subset = ['user'], inplace = True)
        self.user2user_df = self.user2user_df.groupby(['user', 'trail_id'], as_index = False).agg({'rating':'mean'})
        self.user2user_df.fillna(0, inplace = True)
        
    

        
        
class DatabaseExport():
    
    def __init__(self, database):
        
        self.database = database
        self.engine = create_engine('postgresql:///'+self.database)
    
    def database_pandas(self, data, table_name, table_exists = 'append'):
        data.to_sql(table_name, self.engine, if_exists = table_exists)
        

if __name__ == '__main__':
    user_response = input('Grab links or details? ')
    if user_response == 'links':
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
        grabber.grab_name_and_links(states)
    if user_response == 'details':
        conn = psycopg2.connect("dbname='az_trail_recommender' user='josephdope'")
        cur = conn.cursor()
        links_query = "SELECT * FROM links"
        links = sqlio.read_sql_query(links_query, conn)
        links.drop('index', axis = 1, inplace = True)
        grabber = DataGrabber()
        grabber.grab_details(links)
        print('grabbing details')

    
    

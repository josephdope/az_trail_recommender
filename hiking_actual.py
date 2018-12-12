import pandas as pd
import numpy as np
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from sklearn.feature_extraction.text import TfidfVectorizer
from nltk.tokenize import RegexpTokenizer
import time
import psycopg2
from sqlalchemy import create_engine
from collections import defaultdict
import re



def my_tokenizer(doc):
    tokenizer = RegexpTokenizer(r'\w+')
    article_tokens = tokenizer.tokenize(doc.lower())
    return article_tokens


class DataGrabber():
    
    def __init__(self, url, browser = 'Firefox'):
        self.url = url
        self.browser = browser
        self.links_table = None
        self.details_table = None


    def grab_name_and_links(self, num_scrolls):
        self.browser.get(self.url)
        time.sleep(10)
        self.browser.execute_script("document.querySelector('#fullscreen-search-results > ul:nth-child(3)').scrollTo(0, 10000)")
        for _ in range(num_scrolls):
            self.browser.execute_script("document.querySelector('#fullscreen-search-results > ul:nth-child(3)').scrollBy(0, 450)")
            time.sleep(1)
        page_content = BeautifulSoup(self.browser.page_source, "html.parser")
        X = page_content.findAll('h3', attrs = {'class':'name'})
        names = []
        links = []
        for i in X:
            names.append(i.attrs['title']) 
            link = i.find('a')
            links.append(link.attrs['href'][8:])   
        self.links_table = pd.concat((pd.Series(names), pd.Series(links)), axis = 1)
        self.links_table.columns = ['trail', 'link']
        
    
    def grab_details(self):
        trail_dict = defaultdict(list)
        for t in self.links_table.iterrows():
            try:
                url = 'https://www.alltrails.com/'+t[1][2][9:]
                print(url)
                self.browser.get(url)
                page_content = BeautifulSoup(self.browser.page_source, 'html.parser')
                details = page_content.findAll('div', attrs = {'class':'detail-data'})
                trail_info = []
                trail_info.append(t[1][0])
                trail_info.append(t[1][1])
                for p in details:
                    trail_info.append(p.text)
                trail_info.append(page_content.findAll('div', attrs = {'id':'difficulty-and-rating'})[0].find('span').text)
                trail_info.append(page_content.findAll('span' , attrs = {'class':'number'})[0].text)
                lat = page_content.findAll('meta', attrs = {'itemprop':'latitude'})
                trail_info.append(float(lat[0].attrs['content']))
                long = page_content.findAll('meta', attrs = {'itemprop':'longitude'})
                trail_info.append(float(long[0].attrs['content']))
                tags_results = page_content.findAll('span', attrs = {'class':'big rounded active'})
                tags = []
                for tag in tags_results:
                    tags.append(tag.text)
                tags = ','.join(tags)
                trail_info.append(tags)
                trail_info.append(page_content.findAll('section', attrs = {'id':'trail-top-overview-text'})[0].find('p').text)
                try:
                    trail_info.append(page_content.findAll('div', attrs = {'id':'trail-detail-item'})[0].find('p').text)
                except:
                    trail_info.append(' ')
                trail_dict[t[1][0]] = trail_info
                time.sleep(.5)
                print(t[1][1] + ' information added successfully')
            except:
                print(t[1][1] + ' trail page not found')
                continue
            self.details_table = pd.DataFrame.from_dict(trail_dict, orient = 'index', columns = ['trail_id', 'trail_name', 'dist', 'elev', 'type', 'difficulty', 'num_completed','latitude', 'longitude' ,'tags', 'overview', 'full_desc'])
            
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
            
            

class DatabaseExport():
    
    def __init__(self, data, database, table_name):
        self.data = data
        self.table_name = table_name
        self.database = database
    
    def database_it(self, table, table_name):
        engine = create_engine('postgresql://josephdoperalski@localhost:5432/'+self.database)
        table.to_sql(table_name, engine)
        
            
    
class DataShaper():
    
    def __init__(self, raw_dataframe):
        self.raw = raw_dataframe
        self.proper_df = pd.DataFrame()
        
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
        tags_df = pd.DataFrame(np.zeros((self.proper_df.shape[0], len(tags_set))), columns = tags_set, index = self.proper_df['trail_id'])
        
    def tfidf(self, tokenizer = my_tokenizer):
        vect = TfidfVectorizer(tokenizer = tokenizer, stop_words = 'english', ngram_range = (1,2), min_df = .02)
        tfidf_init = vect.fit_transform(self.proper_df['text'])
        tfidf_df = pd.DataFrame(tfidf_init.toarray(), columns = vect.get_feature_names(), index = self.proper_df.index)
        self.proper_df = pd.concat((self.proper_df.drop(['text'], axis = 1), tfidf_df), axis = 1)
        return tfidf_df
        
        

        
        
class DatabaseExport():
    
    def __init__(self, database):
        
        self.database = database
        self.engine = create_engine('postgresql://josephdoperalski@localhost:5432/'+self.database)
    
    def database_pandas(self, data, table_name):
        data.to_sql(table_name, self.engine)
        

if __name__ == '__main__':
    print('good')
#    url = 'https://www.alltrails.com/trail/us/arizona/piestewa-peak-summit-trail-300'
#    browser = webdriver.Firefox(executable_path='/usr/local/bin/geckodriver')
#    browser.get(url)
#    page_content = BeautifulSoup(browser.page_source, "html.parser")
#    details = page_content.findAll('div', attrs = {'class':'detail-data'})
#    print(details)
#    trail_info = []
#    for p in details:
#        trail_info.append(p.text)
#    pop = page_content.findAll('span' , attrs = {'class':'number'})  
#    print(page_content.findAll('div', attrs = {'id':'trail-detail-item'})[0].find('p').text)
#    print(page_content.findAll('section', attrs = {'id':'trail-top-overview-text'})[0].find('p').text)
            
#    print(' '.join(page_content.findAll('span', attrs = {'class':'big rounded active'}).text))
#    tags = page_content.findAll('span', attrs = {'class':'big rounded active'})
#    ' '.join(tags.find('p').text)
    
#    tags_results = page_content.findAll('span', attrs = {'class':'big rounded active'})
#    tags = []
#    for tag in tags_results:
#        tags.append(tag.text)
#    ' '.join(tags)   
#    
#    
#    trail_dict = defaultdict(list)
#    page_content = BeautifulSoup(browser.page_source, 'html.parser')
#    details = page_content.findAll('div', attrs = {'class':'detail-data'})
#    trail_info = []
#    for p in details:
#        trail_info.append(p.text)
#    trail_info.append(page_content.findAll('span' , attrs = {'class':'number'})[0].text)
#    tags_results = page_content.findAll('span', attrs = {'class':'big rounded active'})
#    print(page_content.findAll('div', attrs = {'id':'difficulty-and-rating'})[0].find('span').text)
#    tags = []
#    for tag in tags_results:
#        tags.append(tag.text)
#    tags = ' '.join(tags)
#    trail_info.append(tags)
#    trail_info.append(page_content.findAll('section', attrs = {'id':'trail-top-overview-text'})[0].find('p').text)
#    trail_info.append(page_content.findAll('div', attrs = {'id':'trail-detail-item'})[0].find('p').text)
#    trail_dict[0] = trail_info


    
    

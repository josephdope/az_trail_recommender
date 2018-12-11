import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import time


#
url = 'https://www.alltrails.com/explore?b_tl_lat=35.58138418324621&b_tl_lng=-115.12573242187499&b_br_lat=31.924192605327708&b_br_lng=-107.65502929687499&a[]=hiking'
option = webdriver.ChromeOptions()
url_test = 'https://www.alltrails.com/explore/us/arizona/tempe?a[]=hiking'
option.add_argument(" — incognito")
#browser = webdriver.Chrome(executable_path='/usr/local/bin/chromedriver', chrome_options=option)

browser = webdriver.Firefox(executable_path='/usr/local/bin/geckodriver')

browser.get(url)
time.sleep(10)

elem = browser.find_element_by_id('fullscreen-search-results')

#actions = ActionChains(browser)
#actions.move_to_element(elem).perform()
#ebrowser.execute_script('alert("Starting up")')
time.sleep(1)
browser.execute_script("document.querySelector('#fullscreen-search-results > ul:nth-child(3)').scrollTo(0, 10000)")
                                               
for _ in range(1000):
    browser.execute_script("document.querySelector('#fullscreen-search-results > ul:nth-child(3)').scrollBy(0, 450)")
    time.sleep(1)


#browser.execute_script()
#
##browser.find_element_by_xpath('//ul').click()

#for i in range(5):
#    # Scroll page down
#    browser.find_element_by_id('fullscreen-search-results').send_keys(Keys.END)
#    time.sleep(2)
#
#elem = browser.find_element_by_class_name('sortable')

#browser.execute_script("window.scrollTo(0, 4060 )")

#actions = ActionChains(browser);
#actions.moveToElement(elem);
#actions.click();
#actions.sendKeys(Keys.PAGE_DOWN)
#actions.build().perform();

#no_of_pagedowns = 1000

#while no_of_pagedowns:
#    browser.send_keys(Keys.PAGE_DOWN)
#    time.sleep(0.5)
#    no_of_pagedowns-=1
#
#post_elems = browser.find_elements_by_tag_name('ul')



    
#page_response = requests.get(browser, timeout=5)
page_content = BeautifulSoup(browser.page_source, "html.parser")



X = page_content.findAll('h3', attrs = {'class':'name'})

names = []
links = []
for i in X:
    names.append(i.attrs['title'])
    link = i.find('a')
    links.append(link.attrs['href'])
    

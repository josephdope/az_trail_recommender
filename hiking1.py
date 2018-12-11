import requests
from bs4 import BeautifulSoup

#url = 'https://www.alltrails.com/us/arizona/hiking'
#page_response = requests.get(url, timeout=5)
#page_content = BeautifulSoup(page_response.content, "html.parser")

#print(page_content)

X = page_content.findAll('h3','name')

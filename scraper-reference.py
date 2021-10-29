from bs4 import BeautifulSoup
from selenium import webdriver 
from selenium.webdriver.chrome.options import Options

import re
import urllib
import time
import json


def get_js_soup(url,driver):
    try:
        driver.set_page_load_timeout(5) # Set timeout to 5 sec
        driver.get(url)
        res_html = driver.execute_script('return document.body.innerHTML')
        soup = BeautifulSoup(res_html,'html.parser') #beautiful soup object to be used for parsing html content
        return soup
    except Exception as e:
        soup = 'error' + str(e)
        return soup


# create a webdriver object and set options for headless browsing
options = Options()
options.headless = True
initial_url = 'https://docs.python.org/3.10/contents.html'
driver = webdriver.Chrome(executable_path=".\chromedriver", options=options)

# Parse base url to college_link_url
print ('-'*10,'Parse Python base url')
directory_base_url = 'https://docs.python.org/3.10/'
doc_url_list = []
doc_title_list = []

soup = get_js_soup(initial_url,driver)

soup_area = soup.find('div',class_='toctree-wrapper compound') # Step 1: div class="toctree-wrapper compound"
# print(soup_area)

for link_holder in soup_area.find_all('a', class_='reference internal'): # Step 2: Get link (class="reference internal")
    doc_link = link_holder.get('href')
    doc_title = link_holder.get_text()
    doc_url = directory_base_url + doc_link

    doc_url_list.append(doc_url)
    doc_title_list.append(doc_title)

print ("total", len(doc_url_list), "links")


json_doc = []

for i, link in enumerate(doc_url_list):
    doc_url = link
    doc_title = doc_title_list[i]
    soup = get_js_soup(doc_url,driver)

    doc_url_array = doc_url.split('#')
    
    print (i, "is in progress", doc_url)
    
    if (len(doc_url_array) == 1):
        soup_text = soup.find('div', class_='section').text
    else:
        # print ("anchor:", doc_url_array[1])
        soup_text = soup.find('div', id=doc_url_array[1]).text
    
    soup_text = soup_text.replace("\n", " ")

    doc_dictionary = {}
    doc_dictionary['title'] = doc_title
    doc_dictionary['text'] = soup_text
    doc_dictionary['url'] = doc_url

    json_doc.append(doc_dictionary)
    

    '''
    if (i == 2):
        break
    '''

print ("writing to json")
with open("reference_doc.json", "w", encoding = 'utf8') as json_file:
    json.dump(json_doc, json_file, indent=4, ensure_ascii=False)
print ("job finished")
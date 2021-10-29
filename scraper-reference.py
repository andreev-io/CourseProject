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
initial_url = 'https://docs.python.org/3/contents.html'
driver = webdriver.Chrome(executable_path=".\chromedriver", options=options)

# Parse base url to directory_base_url
print ('-'*10,'Parse Python base url')
directory_base_url = 'https://docs.python.org/3/'
doc_url_list = []
doc_title_list = []

soup = get_js_soup(initial_url,driver)

# Step 1: Collect links from the TOC
soup_area = soup.find('div',class_='toctree-wrapper compound') # Step 1-1: div class="toctree-wrapper compound"
# print(soup_area)

for link_holder in soup_area.find_all('a', class_='reference internal'): # Step 1-2: Get the URL link and title (class="reference internal")
    doc_link = link_holder.get('href')
    doc_title = link_holder.get_text()
    doc_url = directory_base_url + doc_link

    # Step 1-3: Append parsed link to doc_url_list(URL link) and doc_title_list (Title)
    doc_url_list.append(doc_url)
    doc_title_list.append(doc_title)

print ("total", len(doc_url_list), "links")


# Step 2: Crawl text from links

json_doc = []

for i, link in enumerate(doc_url_list):
    doc_url = link
    doc_title = doc_title_list[i]
    soup = get_js_soup(doc_url,driver)

    doc_url_array = doc_url.split('#') # Step 2-1: Parse anchor and page from the link
    
    print (i, "is in progress", doc_url)
    
    if (len(doc_url_array) == 1): # Step 2-2-1: If the link does not have an anchor(length = 1)
        soup_text = soup.find('div', class_='section').text # Crawl the entire page (class='section')
    else: # Step 2-2-2: If the link has an anchor(length = 2)
        # print ("anchor:", doc_url_array[1])
        soup_text = soup.find('div', id=doc_url_array[1]).text # Crawl the anchor part only (id=anchor)
    
    soup_text = soup_text.replace("\n", " ")

    doc_dictionary = {}
    doc_dictionary['title'] = doc_title
    doc_dictionary['text'] = soup_text
    doc_dictionary['url'] = doc_url

    # Step 2-3: Append crawl data to json array
    json_doc.append(doc_dictionary)
    

    # (Optional) Crawling stop counter
    '''
    if (i == 2):
        break
    '''

# Step 3: Write to JSON (encoding to UTF-8, but avoid unicode escape charater by ensure_ascii=False)
print ("writing to json")
with open("reference_doc.json", "w", encoding = 'utf8') as json_file:
    json.dump(json_doc, json_file, indent=4, ensure_ascii=False)
print ("job finished")
import re
import urllib
import time
import json

from bs4 import BeautifulSoup
from selenium import webdriver 
from selenium.webdriver.chrome.options import Options
from urllib.parse import urlparse


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

# Basic variable setup
base_url_list = []
doc_url_list = []
doc_title_list = []
StopCounter = 0

# Parse base url to directory_base_url
print ('Start crawling')
directory_base_url = 'https://docs.python.org/3/'
soup = get_js_soup(initial_url,driver)

# Step 1: Collect links from the TOC (div class="toctree-wrapper compound")
soup_area = soup.find('div',class_='toctree-wrapper compound')

# Step 1-2: Get the URL link and title (class="reference internal")
for link_holder in soup_area.find_all('a', class_='reference internal'): 
    StopCounter += 1
    doc_link = link_holder.get('href')
    doc_title = link_holder.get_text()
    doc_url = directory_base_url + doc_link

    # Step 1-3: Append parsed link to doc_url_list(URL link) and doc_title_list (Title)
    doc_url_array = doc_url.split('#') # Step 1-3-1: Parse anchor and page from the link

    if (len(doc_url_array) == 1): # Step 1-3-2: Exclude anchor link
        base_url_list.append(doc_url)
        doc_url_list.append(doc_url)
        doc_title_list.append(doc_title)
        print ('Found TOC link and title: ', doc_url, doc_title)
    
    # StopCounter
    # if (StopCounter == 3):
    #    break


print ("total", len(doc_url_list), "TOC links found")

# Step 2: Parse anchor and header links
StopCounter = 0
print ('-'*10,'Parsing anchor and header liks')

# Step 2-1:
for i, link in enumerate(base_url_list): 
    StopCounter += 1
    base_url = link
    doc_title = doc_title_list[i]
    soup = get_js_soup(base_url,driver)

    # Step 2-2: filtering text body (div class="body")
    soup_area = soup.find('div',class_='body') 
    print (i, ' Analyzing ', link)
    
    # Step 2-3: Get the URL link and title (class="headerlink")
    for link_holder in soup_area.find_all('a', class_='headerlink'): 
        doc_link = link_holder.get('href')
        doc_title = doc_link.replace('-', ' ')
        doc_title = doc_title.replace('#', '')
        doc_url = base_url + doc_link
        doc_url_list.append(doc_url)
        doc_title_list.append(doc_title)
        # print ('Found TOC link and title: ', doc_url, doc_title)

print ("total", len(doc_url_list), "links found")


# Step 3: Crawl text from links
json_doc = []

for i, link in enumerate(doc_url_list):
    doc_url = link
    doc_title = doc_title_list[i]
    soup = get_js_soup(doc_url,driver)

    doc_url_array = doc_url.split('#') # Step 3-1: Parse anchor and page from the link
    
    print (i, "is in progress", doc_url)
    
    if (len(doc_url_array) == 1): # Step 3-2-1: If the link does not have an anchor(length = 1)
        try:
            soup_text = soup.find('div', class_='section').text # Crawl the entire page (class='section')
        except Exception: # For any parse error, then ignore (broken link is very common)
            pass
    else: # Step 2-2-2: If the link has an anchor(length = 2)
        # print ("anchor:", doc_url_array[1])
        try:
            if soup.find('div', id=doc_url_array[1]):
                soup_text = soup.find('div', id=doc_url_array[1]).text # Crawl the anchor part only (id=anchor)
            else:
                soup_find = soup.find('dt', id=doc_url_array[1]) # Crawl the anchor part only (id=anchor)
                soup_text = soup_find.find_next_sibling("dd").text
        except Exception: # For any parse error, then ignore (broken link is very common)
            pass
    
    soup_text = soup_text.replace("\n", " ")
    soup_text = soup_text.replace('\"', '\'')

    doc_dictionary = {}
    doc_dictionary['title'] = doc_title
    doc_dictionary['text'] = soup_text
    doc_dictionary['url'] = doc_url

    # Step 2-3: Append crawl data to json array
    json_doc.append(doc_dictionary)

# Step 4: Write to JSON (encoding to UTF-8, but avoid unicode escape charater by ensure_ascii=False)
print ("writing to JSON and link")
with open("reference_doc.json", "w", encoding = 'utf8') as json_file:
    json.dump(json_doc, json_file, indent=4, ensure_ascii=False)
with open("reference_link.txt", "w", encoding = 'utf8') as link_text:
    for link in doc_url_list:
        link_text.write(link + "\n")
print ("job finished")
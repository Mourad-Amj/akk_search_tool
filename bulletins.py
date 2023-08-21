import requests
from bs4 import BeautifulSoup as bs
import re
import pandas as pd
from lxml import etree
import json
import tqdm
import ssl
ssl._create_default_https_context = ssl._create_unverified_context

def clean_unicode(text):
    return text.encode('utf-8').decode('unicode_escape')

ROOT_URL = "https://www.lachambre.be/kvvcr/showpage.cfm?&language=fr&cfm=/site/wwwcfm/qrva/qrvaList.cfm?legislat=55"
LINK_PREFIX = "https://www.lachambre.be"

response = requests.get(ROOT_URL)
soup = bs(response.text, "html.parser")

contenu_links = ['https://www.lachambre.be/kvvcr/showpage.cfm?&language=fr&cfm=/site/wwwcfm/qrva/qrvatoc.cfm?legislat=55&bulletin=B113']
 
"""contenu_link = soup.find_all("a")
for link in contenu_link:
    href = link.get("href")
    if href.startswith("showpage.cfm?&language=fr&cfm=/site/wwwcfm/qrva/qrvatoc.cfm"):
        full_link = LINK_PREFIX + "/kvvcr/" + href
        if full_link not in contenu_links:
            contenu_links.append(full_link)"""


data_list = []
for main_link in tqdm.tqdm(contenu_links):
    main_response = requests.get(main_link)
    main_soup = bs(main_response.text, "html.parser")
    
    links = main_soup.find_all("div", class_=["linklist_0", "linklist_1"])
    for div in links:
        link = div.find("a")
        if link is not None:
            href = link.get("href")
            full_link = LINK_PREFIX + "/kvvcr/" + href
            
            response = requests.get(full_link)
            soup = bs(response.text, "html.parser")
            
            title = clean_unicode(soup.find("h1").text.strip())
        
            data = {
                'Full_link': full_link,
                'Title': title
            }
            
    data_list.append(data)

with open ("data/bulletin.json","w", encoding="utf-8") as f:
    json.dump(data, f, indent=4, ensure_ascii=False)
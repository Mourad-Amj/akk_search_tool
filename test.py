import requests
from bs4 import BeautifulSoup as bs
import re
import pandas as pd
from lxml import etree
import ssl
ssl._create_default_https_context = ssl._create_unverified_context

ROOT_URL = f"https://www.lachambre.be/kvvcr/showpage.cfm?&language=fr&cfm=/site/wwwcfm/qrva/qrvaList.cfm?legislat=55"
LINK_PREFIX = "https://www.lachambre.be"

response = requests.get(ROOT_URL)
soup = bs(response.text, "html.parser")

pdf_links = []
for link in soup.find_all('a', href=True):
    if link['href'].endswith('pdf') and link['href'].startswith("/QRVA"):
        full_link = LINK_PREFIX + link['href']
        if full_link not in pdf_links:
            pdf_links.append(full_link)
            
contenu_links = [] 
contenu_link = soup.find_all("a")
for link in contenu_link:
    href = link.get("href")
    if href.startswith("showpage.cfm?&language=fr&cfm=/site/wwwcfm/qrva/qrvatoc.cfm"):
        full_link = LINK_PREFIX + "/kvvcr/" + href
        if full_link not in contenu_links:
            contenu_links.append(full_link)
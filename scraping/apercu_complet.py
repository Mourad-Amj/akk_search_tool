import requests
import json
from bs4 import BeautifulSoup as bs
import json
import pandas as pd


def get_soup(url: str):
    response = requests.get(url)
    return bs(response.content, "html.parser")


url = 'https://www.lachambre.be/kvvcr/showpage.cfm?section=/flwb&language=fr&cfm=ListDocument.cfm'
base_url = 'https://www.lachambre.be/kvvcr/'

soup = get_soup(url)

group_links = soup.find_all('a', attrs={'class': 'link'})

document_urls = [base_url + link['href'] for link in group_links]

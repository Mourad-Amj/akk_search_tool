import requests
from bs4 import BeautifulSoup as bs
import json
from tqdm import tqdm as progress_bar
import ssl
from functools import partial
from tqdm.contrib.concurrent import thread_map
from itertools import chain
import pandas as pd
import re
import fire
from fake_useragent import UserAgent
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
import pymongo
import os
import certifi
ssl._create_default_https_context = ssl._create_unverified_context
model = SentenceTransformer('LaBSE')

load_dotenv()
connection = os.getenv("MONGODB_URI")
client = pymongo.MongoClient(connection, tlsCAFile=certifi.where())
db = client["akkanto_db"]
col = db["bulletin_test"]

LINK_PREFIX = "https://www.lachambre.be"

def clean_unicode(text):
    return text.encode('utf-8').decode('latin-1')

def get_all_urls(root_url, session):
    response = session.get(root_url)
    if response.status_code != 200:
        print(f"Error fetching1: {root_url}. Status code: {response.status_code}")
        return

    soup = bs(response.text, "html.parser")
    contenu_link = soup.find_all("a")
    for link in contenu_link:
        href = link.get("href")
        if href.startswith("showpage.cfm?&language=fr&cfm=/site/wwwcfm/qrva/qrvatoc.cfm") or href.startswith("showpage.cfm?&language=nl&cfm=/site/wwwcfm/qrva/qrvatoc.cfm"):
            yield LINK_PREFIX + "/kvvcr/" + href

def scrape_url(url, session):
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
    response = session.get(url, headers=headers)
    if response.status_code != 200:
        print(f"Error fetching2: {url}. Status code: {response.status_code}")
        return

    soup = bs(response.text, "html.parser")
    links = soup.find_all("div", class_=["linklist_0", "linklist_1"])

    for link in links:
        a = link.find('a')
        if a is not None:
            yield f'{LINK_PREFIX}/kvvcr/{a.get("href")}'
    
def formatted_data_fr(data):    
    fr_data = {
            "fr_title": data["Titre"],
            "document_number": data["title"],
            "date": data["Date de délai"],
            "document_page_url": data["page_url"],
            "fr_main_title": data["Question"],
            "link_to_document": data.get("Publication question", "") or data.get("Publication réponse", ""),
            "fr_keywords": data.get("Mots-clés libres", ""),
            "fr_source": "Bulletins des questions et réponses écrites",
            "commissionchambre": data["Département"],
            "fr_text": data.get("Réponse", ""),
            "fr_stakeholders": data.get("Auteur", ""),
            "fr_status": data["Statut question"],
            "fr_title_embedding": [],
            "fr_text_embedding": [],
            "descripteurEurovocprincipal": data.get("Desc. Eurovoc principal", ""),
            "descripteursEurovoc": data.get("Descripteurs Eurovoc", ""),
        }   

    existing_document = col.find_one({"document_number": fr_data["document_number"],"fr_source":"Bulletins des questions et réponses écrites"})

    if existing_document:
        print("Document with the same doc_number already exists.") 
    
    else:
        keywords = []
        if fr_data["descripteurEurovocprincipal"] in fr_data.values():
            keywords.append(fr_data["descripteurEurovocprincipal"].title()) 
        if fr_data["descripteursEurovoc"] in fr_data.values():
            descripteurs = fr_data["descripteursEurovoc"].title().split('|')
            keywords.extend(descripteurs)
        if fr_data["fr_keywords"] in fr_data.values():
            descripteurs = fr_data["fr_keywords"].title().split('|')
            keywords.extend(descripteurs)
        formatted_list = []
        for item in keywords:
            cleaned_item = item.strip()
            if " " in cleaned_item:
                cleaned_item = cleaned_item.title()
            else:
                cleaned_item = cleaned_item.capitalize()
            formatted_list.append(cleaned_item)
        fr_data["fr_keywords"] = list(set(formatted_list))

        policy_level = fr_data["commissionchambre"].title()
        fr_data["policy_level"] = f'Federal Parliament ({policy_level})'

        
        def embed(text, model):
            text_embedding = model.encode(text)
            return text_embedding
        
        fr_data["fr_title_embedding"] = embed(fr_data["fr_main_title"], model=model).tolist()
        fr_data["fr_text_embedding"] = embed(fr_data["fr_text"], model=model).tolist()

        col.insert_one(fr_data)
    #return fr_data

def formatted_data_nl(data):    
    nl_data = {
            "nl_title": data["Titel"],
            "document_number": data["title"],
            "date": data.get("Termijndatum", ""),
            "document_page_url": data["page_url"],
            "nl_main_title": data["Vraag"],
            "link_to_document": data.get("Publicatie vraag", "") or data.get("Publicatie antwoord", ""),
            "nl_keywords": data.get("Vrije trefwoorden", ""),
            "nl_source": "Bulletins vragen en antwoorden",
            "commissionchambre": data["Departement"],
            "nl_text": data.get("Antwoord", ""),
            "nl_stakeholders": data.get("Auteur", ""),
            "nl_status": data["Status vraag"],
            "nl_title_embedding": [],
            "nl_text_embedding": [],
            "descripteurEurovocprincipal": data.get("Eurovoc-hoofddescriptor", ""),
            "descripteursEurovoc": data.get("Eurovoc-descriptoren", ""),
        } 
    
    existing_document = col.find_one({"document_number": nl_data["document_number"],"nl_source":"Bulletins vragen en antwoorden"})

    if existing_document:
        print("Document with the same doc_number already exists.") 

    else:
        keywords = []
        if nl_data["descripteurEurovocprincipal"] in nl_data.values():
            keywords.append(nl_data["descripteurEurovocprincipal"].title()) 
        if nl_data["descripteursEurovoc"] in nl_data.values():
            descripteurs = nl_data["descripteursEurovoc"].title().split('|')
            keywords.extend(descripteurs)
        if nl_data["nl_keywords"] in nl_data.values():
            descripteurs = nl_data["nl_keywords"].title().split('|')
            keywords.extend(descripteurs)
        formatted_list = []
        for item in keywords:
            cleaned_item = item.strip()
            if " " in cleaned_item:
                cleaned_item = cleaned_item.title()
            else:
                cleaned_item = cleaned_item.capitalize()
            formatted_list.append(cleaned_item)
        nl_data["nl_keywords"] = list(set(formatted_list))

        policy_level = nl_data["commissionchambre"].title()
        nl_data["policy_level"] = f'Federal Parliament ({policy_level})'
        
        def embed(text, model):
            text_embedding = model.encode(text)
            return text_embedding
        nl_data["nl_title_embedding"] = embed(nl_data["nl_main_title"], model=model).tolist()
        nl_data["nl_text_embedding"] = embed(nl_data["nl_text"], model=model).tolist()

        col.insert_one(nl_data)

def scrapping_data(full_link, session):

    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
    response = session.get(full_link, headers=headers)
    if response.status_code != 200:
        print(f"Error fetching3: {full_link}. Status code: {response.status_code}")
        return
    soup = bs(response.text, "html.parser")

    title = clean_unicode(soup.find("h1").text.strip())
    data_dict = {"page_url": full_link, "title": title}

    document_table = soup.find("table")

    if document_table is None:
        return list()
    
    df = pd.read_html(response.text)[0]
    data_dict.update({k:v for k,v in df.to_dict(orient='tight')['data'][1:]})
    
    match = re.match(pattern='legislat=(\d+)', string=full_link)
    if match is not None:
        legislature = match.group(1)
        for header in ("Publication question", "Publication réponse"):
            if header in data_dict and len(data_dict[header]) > 0: 
                file = data_dict[header][1:]
                data_dict[header] = f"https://www.lachambre.be/QRVA/pdf/{legislature}/{legislature}K0{file}.pdf"

    return formatted_data_fr(data_dict)


def main(language='fr'):
    root_url = f"https://www.lachambre.be/kvvcr/showpage.cfm?&language={language}&cfm=/site/wwwcfm/qrva/qrvaList.cfm?legislat=55"

    with requests.Session() as session :
        links = set(get_all_urls(root_url, session))
        full_links = chain.from_iterable(thread_map(partial(scrape_url, session=session), links))
        print("done getting full links")
        all_data = list(map(partial(scrapping_data, session=session), progress_bar(full_links))) # 1h30 total time
"""    with open(f"data/bulletin_{language}.json", "w", encoding="utf-8") as f:
        json.dump(all_data, f, indent=4, ensure_ascii=False)"""

if __name__ == "__main__":
    fire.Fire(main)

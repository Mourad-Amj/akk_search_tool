import requests
from bs4 import BeautifulSoup as bs
import json
import tqdm 
import ssl
from functools import partial
from tqdm.contrib.concurrent import thread_map
import sys
from itertools import chain
import pandas as pd
import re
import fire

ssl._create_default_https_context = ssl._create_unverified_context

LINK_PREFIX = "https://www.lachambre.be"

def clean_unicode(text):
    return text.encode('utf-8').decode('latin-1')

def get_all_urls(root_url, session):
    response = session.get(root_url)

    soup = bs(response.text, "html.parser")
    contenu_link = soup.find_all("a")
    for link in contenu_link:
        href = link.get("href")
        if href.startswith("showpage.cfm?&language=fr&cfm=/site/wwwcfm/qrva/qrvatoc.cfm"):
            yield LINK_PREFIX + "/kvvcr/" + href

def scrape_url(url, session):
    response = session.get(url)
    soup = bs(response.text, "html.parser")
    links = soup.find_all("div", class_=["linklist_0", "linklist_1"])

    for link in links:
        a = link.find('a')
        if a is not None:
            yield f'{LINK_PREFIX}/kvvcr/{a.get("href")}'
    
def formatted_data_fr(data):    
    return {
            "title": data["Question"],
            "document_number": data["title"],
            "date": data["Date de délai"],
            "document_page_url": data["page_url"],
            "main_title": data["titre"],
            "link_to_document": data.get("Publication question", "") or data.get("Publication réponse", ""),
            "keywords": data.get("Mots-clés libres", ""),
            "source": "",
            "commissionchambre": data["Département"],
            "fr_text": data.get("Réponse", ""),
            "nl_text": "",
            "stakeholders": data["Auteur"],
            "status": data["Statut question"],
            "title_embedding": [],
            "fr_text_embedding": [],
            "nl_text_embedding": [],
            "topic": "",
            "policy level": "",
            "type": "",
            "issue": "",
            "reference": "",
            "maindocuments": "",
            "typededocument": "",
            "descripteurEurovocprincipal": data.get("Desc. Eurovoc principal", ""),
            "descripteursEurovoc": data.get("Descripteurs Eurovoc", ""),
            "seancepleinierechambre": "",
            "compétence": "",
            "1_commissionchambre": "",
            "2_commissionchambre": "",
            "1_seancepleinierechambre": "",
            "2_seancepleinierechambre": "",
        }    

def formatted_data_nl(data):    
    return {
            "title": data["Vraag"],
            "document_number": data["title"],
            "date": data["Termijndatum"],
            "document_page_url": data["page_url"],
            "main_title": data["Titel"],
            "link_to_document": data.get("Publicatie vraag", "") or data.get("Publicatie antwoord", ""),
            "keywords": data.get("Vrije trefwoorden", ""),
            "source": "",
            "commissionchambre": data["Departement"],
            "fr_text": data.get("Antwoord", ""),
            "nl_text": "",
            "stakeholders": data["Auteur"],
            "status": data["Status vraag"],
            "title_embedding": [],
            "fr_text_embedding": [],
            "nl_text_embedding": [],
            "topic": "",
            "policy level": "",
            "type": "",
            "issue": "",
            "reference": "",
            "maindocuments": "",
            "typededocument": "",
            "descripteurEurovocprincipal": data.get("Eurovoc-hoofddescriptor", ""),
            "descripteursEurovoc": data.get("Eurovoc-descriptoren", ""),
            "seancepleinierechambre": "",
            "compétence": "",
            "1_commissionchambre": "",
            "2_commissionchambre": "",
            "1_seancepleinierechambre": "",
            "2_seancepleinierechambre": "",
        } 

def scrapping_data(full_link, session) :
    print(full_link)
    response = session.get(full_link)
    soup = bs(response.text, "html.parser")

    title = clean_unicode(soup.find("h1").text.strip())
    data_dict = {"page_url": full_link, "title": title}

    document_table = soup.find("table")

    if document_table is None:
        return list()
    
    df = pd.read_html(response.text)[0]
    data_dict.update({k:v for k,v in df.to_dict(orient='tight')['data'][1:]})
    
    legislature = re.match('legislat=(\d+)').group(1)
    for header in ("Publication question", "Publication réponse"):
        if header in data_dict: 
            file = data_dict[header][1:]
            data_dict[header] = f"https://www.lachambre.be/QRVA/pdf/{legislature}/{legislature}K0{file}.pdf"

    return formatted_data_fr(data_dict)


def main(language='fr'):
    root_url = f"https://www.lachambre.be/kvvcr/showpage.cfm?&language={language}&cfm=/site/wwwcfm/qrva/qrvaList.cfm?legislat=55"

    with requests.Session() as session :
        links = set(get_all_urls(root_url, session))
        full_links = chain.from_iterable(thread_map(partial(scrape_url, session=session), links))
        all_data = thread_map(partial(scrapping_data, session=session), full_links)
    
    with open(f"data/bulletin_{language}.json", "w", encoding="utf-8") as f:
        json.dump(all_data, f, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    fire.Fire(main)

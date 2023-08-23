"""
Scrape the table data including links to pdfs of documents for
all documents of the 'Apercu Complet' page of the lachambre.be site
"""
import time
import requests
import certifi
import unicodedata
import ssl
import json
from bs4 import BeautifulSoup as bs
import pdfplumber
import io
import re
from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

ssl._create_default_https_context = ssl._create_unverified_context
start_time = time.perf_counter()

from sentence_transformers import SentenceTransformer

model = SentenceTransformer('all-MiniLM-L6-v2')
def embed(main_title, fr_text , nl_text ,model):
    main_title_embedding = model.encode(main_title)
    fr_text_embedding = model.encode(fr_text)
    nl_text_embedding = model.encode(nl_text)
    return main_title_embedding,fr_text_embedding,nl_text_embedding


def get_text_documet_parlementaire(url):
    rq = requests.get(url)
    left_column_text_all_pages = ""
    right_column_text_all_pages = ""

    with pdfplumber.open(io.BytesIO(rq.content)) as pdf:
        for page in pdf.pages:
            words = page.extract_words()
            threshold_x = 300

            left_column_words = [word for word in words if word['x0'] < threshold_x]
            right_column_words = [word for word in words if word['x0'] >= threshold_x]
            left_column_text = ' '.join([word['text'] for word in left_column_words])
            right_column_text = ' '.join([word['text'] for word in right_column_words])
            left_column_text_all_pages += left_column_text + ' '
            right_column_text_all_pages += right_column_text + ' '

            fr_text = re.sub(r'(?<=\w)-(\s)(?=\w)', r'', left_column_text_all_pages) # remove end_line hyphens
            fr_text = re.sub(r'DOC 55 \d{4}/\d{3}', '', fr_text)
            fr_text = re.sub(r'\d{4}/\d{3} DOC 55', '', fr_text)
            fr_text = re.sub(r'CHAMBRE \d+e SESSION DE LA 55e LÉGISLATURE \d{4}(?: \d+)?', '', fr_text)
            nl_text = re.sub(r'(?<=\w)-(\s)(?=\w)', r'', right_column_text_all_pages) # remove end_line hyphens
            nl_text = re.sub(r'DOC 55 \d{4}/\d{3}', '', nl_text)
            nl_text = re.sub(r'\d{4}/\d{3} DOC 55', '', nl_text)
            nl_text = re.sub(r'\d{4} KAMER • \d+e ZITTING VAN DE 55e ZITTINGSPERIODE(?: \d+)?', '', nl_text)

    return fr_text, nl_text    

# print("Connecting to database ...")

# connection = 'mongodb+srv://maximberge:aAIbS7zRpsbsy6Gb@cluster0.p97p1.mongodb.net/?retryWrites=true&w=majority'

# client = MongoClient(connection, tlsCAFile=certifi.where())
# db = client["akkanto_db"]
# collection = db["doc_complets_test"]


def get_soup(url: str):
    response = requests.get(url)
    return bs(response.content, "html.parser")


url = "https://www.lachambre.be/kvvcr/showpage.cfm?section=/flwb&language=fr&cfm=ListDocument.cfm"
base_url = "https://www.lachambre.be/kvvcr/"

soup = get_soup(url)
group_links = soup.find_all("a", attrs={"class": "link"})
group_document_urls = [base_url + link["href"] for link in group_links]

print("Creating list of document data ...")
document_list = []
for group_document_url in group_document_urls[:1]:
    url_soup = get_soup(group_document_url)
    table = url_soup.find("table")
    document_links = table.find_all("a")
    documents = [base_url + link["href"] for link in document_links]
    for index, document in enumerate(documents, start=1):
        print(f"Adding document data {index} of {len(documents)} ...")
        document_soup = get_soup(document)
        document_dict = {}
        section = document_soup.find("div", attrs={"id": "Story"})
        
        document_dict["title"] = section.find("h3").text.strip()
        document_dict["document_number"] = document_dict["title"][-4:]
        document_dict["document_page_url"] = document
        document_dict["main_title"] = section.find("h4").text.strip()
        document_table = section.find("table")
        for rows in document_table.select("tr"):
            cells = rows.find_all("td", recursive=False)
            for cell in cells:
                if cell.find("table"):
                    cell.decompose()
                    continue
                header = " ".join(cells[0].text.split())
                content = " ".join(cells[1].text.split())
            if header == "Document Chambre":
                try:
                    document_dict[header] = rows.find("a").get("href")
                except:
                    document_dict[header] = content
            else:
                document_dict[header] = content
        final_dict = {}
        final_dict["title"] = document_dict["title"]
        final_dict["document_number"] = document_dict["document_number"]

        if "Date de dépôt" in document_dict.keys():
            final_dict["date"] = document_dict["Date de dépôt"]

        final_dict["document_page_url"] = document_dict["document_page_url"]

        final_dict["main_title"] = document_dict["main_title"]

        if "Document Chambre" in document_dict.keys(): 
            final_dict["link_to_document"] = document_dict["Document Chambre"]

        keywords = set()
        if "Descripteur Eurovoc principal" in document_dict.keys():
            keywords.add(document_dict["Descripteur Eurovoc principal"])    
        if "Descripteurs Eurovoc" in document_dict.keys():
            descripteurs = document_dict["Descripteurs Eurovoc"].split('|')
            keywords.update(descripteurs)
        if "Mots-clés libres" in document_dict.keys():
            descripteurs = document_dict["Mots-clés libres"].split('|')
            keywords.update(descripteurs)
        final_dict["keywords"] = list(keywords)

        final_dict["source"] = "Documents parlementaires aperçu complet"

        if "COMMISSION CHAMBRE" in document_dict.keys():
            final_dict["commissionchambre"] = document_dict["COMMISSION CHAMBRE"]
        if "1. COMMISSION CHAMBRE" in document_dict.keys():
            final_dict["commissionchambre"] = document_dict["1. COMMISSION CHAMBRE"]
        try:
            fr_text, nl_text = get_text_documet_parlementaire(final_dict["link_to_document"])
        except:
            fr_text, nl_text = "", ""
        final_dict["stakeholders"] = document_dict["Auteur(s)"]
        final_dict["status"] = ""

        main_title_embedding, fr_text_embedding, nl_text_embedding = embed(final_dict["main_title"], fr_text=fr_text, nl_text=nl_text, model=model)
        final_dict["title_embedding"] = main_title_embedding
        final_dict["fr_text_embedding"] = fr_text_embedding
        final_dict["nl_text_embedding"] = nl_text_embedding

        final_dict["topic"] = ""
        if "commissionchambre" in final_dict.keys():
            policy_level = final_dict["commissionchambre"].capitalize()
            final_dict["policy_level"] = f'Federal Parliament ({policy_level})'
        final_dict["type"] = document_dict["Type de document"]
        final_dict["issue"] = ""
        final_dict["reference"] = ""

       
             
        # query = {
        # "$and": [
        #     {"source": {"$eq": "Documents parlementaires aperçu complet"}},
        #     {"document_number": {"$eq": final_dict['document_number']}}
        # ]
        # }
      

        # if collection.find_one(query):
        #     print("Checking if document already exist in database ...")  
        #     print(f" The document with the number {final_dict['document_number']} already exists.")
        # else:
        #     print(f"Adding document with number {final_dict['document_number']} to the database ...")  
        #     collection.insert_one(final_dict)  
         
      
        # for item in document_list:
        #     print(item)
# print("Closing connection to database ...")
# client.close()

end_time = time.perf_counter()
print(round(end_time - start_time, 2), "seconds")



# with open("data/apercu_complet_partial.json", "w") as fout:
#     json.dump(document_list, fout,ensure_ascii=False)

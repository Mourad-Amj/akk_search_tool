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
import pymongo
import os
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
import numpy as np


ssl._create_default_https_context = ssl._create_unverified_context
start_time = time.perf_counter()

load_dotenv()
connection = os.getenv("MONGODB_URI")
client = pymongo.MongoClient(connection, tlsCAFile=certifi.where())
db = client["akkanto_db"]
col = db["all_documents"]

model = SentenceTransformer('LaBSE')

def get_soup(url: str):
    response = requests.get(url)
    return bs(response.content, "html.parser")

def embed(text, model):
    text_embedding = model.encode(text)
    return text_embedding

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

def get_type(text):
    if text == "Proposition De Loi":
        return "Law Proposal"
    elif text == "Projet De Loi":
        return "Draft Legislation"
    elif text == "Rapport":
        return "Report"
    elif text == "Proposition De Resolution":
        return "Resolution Proposal"
    elif text == "Proposition Reglement":
        return "Regulation Proposal"
    elif text == "Proposition Commiss. D'enquete":
        return "Proposal for Commission of Enquiry"
    elif text == "Proposition De Révision":
        return "Revision Proposal"
    elif text == "Presentation De Candidats":
        return "Presentation of Candidates"
    elif text == "Budget" or  text == "Elections":
        return text
    elif text == "Expose General":
        return "General Overview"
    elif text == "Tableaux Ou Listes":
        return "Charts/Listes"
    elif text == "Proposition De Declaration":
        return "Declaration Proposal"
    elif text == "Farde":
        return "Binder"
    elif text == "Decision Comm. De Concertation":
        return "Concertation Commission Decision"
    elif text == "Accord De Gouvernement":
        return "Government Agreement"
    elif text == "Liste Revision Constitution":
        return "Constitutional Revision List"
    elif text == "Feuilleton De Petitions":
        return "Petitions List"
    elif text == "Texte Adopte":
        return "Text Adopted"
    else:
        return "Other"
    

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
for group_document_url in group_document_urls[]:
    url_soup = get_soup(group_document_url)
    table = url_soup.find("table")
    document_links = table.find_all("a")
    documents = [base_url + link["href"] for link in document_links]
    for index, document in enumerate(documents, start=1):
        print(f"Adding document data {index} of {len(documents)} ...")
        document_soup = get_soup(document)
        document_dict = {}
        section = document_soup.find("div", attrs={"id": "Story"})
        document_dict["fr_title"] = section.find("h3").text.strip()
        document_dict["document_number"] = document_dict["fr_title"][-4:]
        document_dict["document_page_url"] = document
        document_dict["fr_main_title"] = section.find("h4").text.strip()
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
                    document_dict[header] = "NoURLfound"
            else:
                document_dict[header] = content

        existing_document = col.find_one({"document_number": document_dict["document_number"],"fr_source":"Documents Parlementaires Aperçu Complet"})

        if existing_document:
            print("Document with the same doc_number already exists.")
            
        else:
            final_dict = {}
            final_dict["fr_title"] = document_dict["fr_title"]
            final_dict["document_number"] = document_dict["document_number"]

            if "Date de dépôt" in document_dict.keys():
                final_dict["date"] = document_dict["Date de dépôt"]

            final_dict["document_page_url"] = document_dict["document_page_url"]
            final_dict["fr_main_title"] = document_dict["fr_main_title"]

            if "Document Chambre" in document_dict.keys(): 
                final_dict["link_to_document"] = document_dict["Document Chambre"]

            keywords = []
            if "Descripteur Eurovoc principal" in document_dict.keys():
                keywords.append(document_dict["Descripteur Eurovoc principal"].title()) 
            if "Descripteurs Eurovoc" in document_dict.keys():
                descripteurs = document_dict["Descripteurs Eurovoc"].title().split('|')
                keywords.extend(descripteurs)
            if "Mots-clés libres" in document_dict.keys():
                descripteurs = document_dict["Mots-clés libres"].title().split('|')
                keywords.extend(descripteurs)
            formatted_list = []
            for item in keywords:
                cleaned_item = item.strip()
                if " " in cleaned_item:
                    cleaned_item = cleaned_item.title()
                else:
                    cleaned_item = cleaned_item.capitalize()
                formatted_list.append(cleaned_item)
            final_dict["fr_keywords"] = list(set(formatted_list))

            final_dict["fr_source"] = "Documents Parlementaires Aperçu Complet"

            if "COMMISSION CHAMBRE" in document_dict.keys():
                final_dict["commissionchambre"] = document_dict["COMMISSION CHAMBRE"]
            if "1. COMMISSION CHAMBRE" in document_dict.keys():
                final_dict["commissionchambre"] = document_dict["1. COMMISSION CHAMBRE"]

            if "commissionchambre" in final_dict.keys():
                final_dict["commissionchambre"] = final_dict["commissionchambre"].title()
            
            if final_dict["link_to_document"] == "NoURLfound":
                fr_text, nl_text = "",""
                print("noURL")
            else:
                fr_text, nl_text = get_text_documet_parlementaire(final_dict["link_to_document"])
            if "Auteur(s)" in document_dict.keys():
                final_dict["fr_stakeholders"] = document_dict["Auteur(s)"]

            final_dict["fr_title_embedding"] = embed(final_dict["fr_main_title"], model=model).tolist()
            
            try:
                if final_dict["link_to_document"] == "NoURLfound":
                    final_dict["fr_text_embedding"] = np.array([0]*768).astype(np.float32).tolist()
                    final_dict["nl_text_embedding"] = np.array([0]*768).astype(np.float32).tolist()
                else:
                    final_dict["fr_text_embedding"] = embed(fr_text, model=model).tolist()
                    final_dict["nl_text_embedding"] = embed(nl_text, model=model).tolist()
            except PDFSyntaxError:
                print("issue on pdf")
                final_dict["fr_text_embedding"] = np.array([0]*768).astype(np.float32).tolist()
                final_dict["nl_text_embedding"] = np.array([0]*768).astype(np.float32).tolist()

            if "commissionchambre" in final_dict.keys():
                policy_level = final_dict["commissionchambre"].title()
                final_dict["policy_level"] = f'Federal Parliament ({policy_level})'

            fr_type = re.sub(r'\d+', '', document_dict["Type de document"])
            fr_type = ' '.join(word.capitalize() for word in fr_type.split())
            final_dict["fr_type"] = get_type(fr_type)

            print(f"Adding data {index} into database..")

            col.insert_one(final_dict)        
            

end_time = time.perf_counter()
print(round(end_time - start_time, 2), "seconds")


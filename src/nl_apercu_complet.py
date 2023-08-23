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
    if text == "Wetsontwerp":
        return "Law Proposal"
    elif text == "Wetsvoorstel":
        return "Draft Legislation"
    elif text == "Verslag":
        return "Report"
    elif text == "Voorstel Van Resolutie":
        return "Resolution Proposal"
    elif text == "Voorstel Reglement":
        return "Regulation Proposal"
    elif text == "Voorstel Onderzoekscommissie":
        return "Proposal for Commission of Enquiry"
    elif text == "Voorstel Tot Herziening":
        return "Revision Proposal"
    elif text == "Voordracht Van Kandidaten":
        return "Presentation of Candidates"
    elif text == "Begroting":
        return "Budget"
    elif text == "Algemene Toelichting":
        return "General Overview"
    elif text == "Tabellen Of Lijsten":
        return "Charts/Listes"
    elif text == "Voorstel Van Verklaring":
        return "Declaration Proposal"
    elif text == "Kaft":
        return "Binder"
    elif text == "Beslissing Overlegcommissie":
        return "Concertation Commission Decision"
    elif text == "Regeerakkoord":
        return "Government Agreement"
    elif text == "Lijst Grondwetsherziening":
        return "Constitutional Revision List"
    elif text == "Lijst Van Verzoekschriften":
        return "Petitions List"
    elif text == "Aangenomen Tekst":
        return "Text Adopted"
    elif text ==  "Verkiezingen":
        return "Elections"
    else:
        return "Other"

def get_soup(url: str):
    response = requests.get(url)
    return bs(response.content, "html.parser")


url = "https://www.lachambre.be/kvvcr/showpage.cfm?section=/flwb&language=nl&cfm=ListDocument.cfm"
base_url = "https://www.lachambre.be/kvvcr/"

soup = get_soup(url)
group_links = soup.find_all("a", attrs={"class": "link"})
group_document_urls = [base_url + link["href"] for link in group_links]

print("Creating list of document data ...")
document_list = []
for group_document_url in group_document_urls:
    url_soup = get_soup(group_document_url)
    table = url_soup.find("table")
    document_links = table.find_all("a")
    documents = [base_url + link["href"] for link in document_links]
    print("page:",group_document_url)
    for index, document in enumerate(documents, start=1):
        # print(f"Adding document data {index} of {len(documents)} ...")
        document_soup = get_soup(document)
        document_dict = {}
        section = document_soup.find("div", attrs={"id": "Story"})
        document_dict["nl_title"] = section.find("h3").text.strip()
        document_dict["document_number"] = document_dict["nl_title"][-4:]
        document_dict["document_page_url"] = document
        document_dict["nl_main_title"] = section.find("h4").text.strip()
        document_table = section.find("table")
        for rows in document_table.select("tr"):
            cells = rows.find_all("td", recursive=False)
            for cell in cells:
                if cell.find("table"):
                    cell.decompose()
                    continue
                header = " ".join(cells[0].text.split())
                content = " ".join(cells[1].text.split())
            if header == "Document Kamer":
                try:
                    document_dict[header] = rows.find("a").get("href")
                except:
                    document_dict[header] = "NoURLfound"
            else:
                document_dict[header] = content

        existing_record = col.find_one({"fr_source": "Documents Parlementaires Aperçu Complet", "document_number": document_dict["document_number"],  "nl_source": {"$in": ["", None]}})

        if existing_record:

            final_dict = {}
            final_dict["nl_title"] = document_dict["nl_title"]
            final_dict["nl_main_title"] = document_dict["nl_main_title"]

            keywords = []
            if "Eurovoc-hoofddescriptor" in document_dict.keys():
                keywords.append(document_dict["Eurovoc-hoofddescriptor"].title()) 
            if "Eurovoc descriptoren" in document_dict.keys():
                descripteurs = document_dict["Eurovoc descriptoren"].title().split('|')
                keywords.extend(descripteurs)
            if "Vrije trefwoorden" in document_dict.keys():
                descripteurs = document_dict["Vrije trefwoorden"].title().split('|')
                keywords.extend(descripteurs)
            formatted_list = []
            for item in keywords:
                cleaned_item = item.strip()
                if " " in cleaned_item:
                    cleaned_item = cleaned_item.title()
                else:
                    cleaned_item = cleaned_item.capitalize()
                formatted_list.append(cleaned_item)
            final_dict["nl_keywords"] = list(set(formatted_list))

            final_dict["nl_source"] = "Parlementaire Stukken Volledig Overzicht"

            if "COMMISSIE KAMER" in document_dict.keys():
                final_dict["commissiekamer"] = document_dict["COMMISSIE KAMER"]
            if "1. COMMISSIE KAMER" in document_dict.keys():
                final_dict["commissiekamer"] = document_dict["1. COMMISSIE KAMER"]

            if "commissiekamer" in final_dict.keys():
                final_dict["commissiekamer"] = final_dict["commissiekamer"].title()
        
            if "Auteur(s)" in document_dict.keys():
                final_dict["nl_stakeholders"] = document_dict["Auteur(s)"]

            final_dict["nl_title_embedding"] = embed(final_dict["nl_main_title"], model=model).tolist()

            if "commissiekamer" in final_dict.keys():
                policy_level = final_dict["commissiekamer"].title()
                final_dict["policy_level"] = f'Federal Parliament ({policy_level})'

            # nl_type = re.sub(r'\d+', '', document_dict["Document type"])
            # nl_type = ' '.join(word.capitalize() for word in nl_type.split())
            # final_dict["nl_type"] = get_type(nl_type)

            # print(f"Adding data {index} into database..")

            update_result = col.update_one(
                {"_id": existing_record["_id"]},
                {"$set": final_dict}
            )

        # else:
        #     # print(f"Record not found --> document_number: {document_dict['document_number']}")     
            

end_time = time.perf_counter()
print(round(end_time - start_time, 2), "seconds")


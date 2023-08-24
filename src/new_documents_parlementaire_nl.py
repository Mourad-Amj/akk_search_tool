import requests
from bs4 import BeautifulSoup as bs
import json
import numpy as np
import re
from sentence_transformers import SentenceTransformer
import pandas as pd
import pymongo
import os
from dotenv import load_dotenv
import certifi
import tqdm

model = SentenceTransformer('LaBSE')

load_dotenv()
connection = os.getenv("MONGODB_URI")
client = pymongo.MongoClient(connection, tlsCAFile=certifi.where())
db = client["akkanto_db"]
col = db["all_documents"]

ROOT_URL = "https://www.lachambre.be/kvvcr/showpage.cfm?section=/flwb/recent&language=nl&cfm=/site/wwwcfm/flwb/rapweekweekly.cfm?week=4"
LINK_PREFIX = "https://www.lachambre.be/kvvcr/"
PDF_PREFIX = "https://www.lachambre.be"

def embed(text, model):
    text_embedding = model.encode(text)
    return text_embedding

def remove_extra_spaces(s):
    return re.sub(r"\s+", " ", s).strip()


def get_all_data(link, session):
    data = {}
    data_list = []
    regex = r"\d{1,2}/\d{1,2}/\d{1,4}"

    response = session.get(link)
    soup = bs(response.text, "html.parser")

    finding_element = soup.find_all("div", class_="linklist_1")
    for element in finding_element:
        dossier_id_element = element.find("a")
        dossier_id = dossier_id_element.text
        try:
            text_div_element = (
                dossier_id_element.parent.parent.find_next_sibling().find("div")
            )
        except AttributeError:
            continue

        dossier_content_div_text = remove_extra_spaces(text_div_element.text).split(
            "Datum"
        )
        dossier_text = dossier_content_div_text[0]
        dossier_date = dossier_content_div_text[1]
        text = dossier_text.split(".")[0]

        dossier_date_formatted = None
        match = re.search(regex, dossier_date, re.IGNORECASE)
        if match:
            dossier_date_formatted = match[0]

        pdf_link = None
        pdf_link_element = text_div_element.find("a")
        if pdf_link_element["href"].startswith("/site/wwwcfm/flwb/flwbcheckpdf"):
            pdf_link = PDF_PREFIX + pdf_link_element["href"]

        pdf_link_element = dossier_text.split(" ")[-2]

        dossier_type_of_document = dossier_content_div_text[1].split(" ")[3:]
        dossier_type_of_document_formatted = (" ").join(dossier_type_of_document)

        data = {"nl_title": dossier_type_of_document_formatted.title(),
            "document_number": f"{dossier_id}/{pdf_link_element}",
            "nl_main_title": text,
            "nl_source": "Parlementaire Stukken Recente Documenten"}

        existing_record = col.find_one({"fr_source": "Documents Parlementaires Récents", "document_number": data["document_number"],  "nl_source": {"$in": ["", None]}})

        if existing_record:
            data["nl_title_embedding"] = embed(data["nl_main_title"],model).tolist()
            update_result = col.update_one(
                {"_id": existing_record["_id"]},
                {"$set": data}
            )

def save_file(data):
    with open("data/new_documents_parlementaires_recents_nl.json", "w") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


def main():
    print("Starting scrapping...")

    with requests.Session() as session:
        data = get_all_data(ROOT_URL, session)

    # save_file(data)
    print("Finished")


if __name__ == "__main__":
    main()

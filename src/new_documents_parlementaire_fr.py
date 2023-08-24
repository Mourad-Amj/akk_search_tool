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

ROOT_URL = "https://www.lachambre.be/kvvcr/showpage.cfm?section=/flwb/recent&language=fr&cfm=/site/wwwcfm/flwb/rapweekweekly.cfm?week=4"
LINK_PREFIX = "https://www.lachambre.be/kvvcr/"
PDF_PREFIX = "https://www.lachambre.be"

def embed(main_title, model):

    main_title_embedding = model.encode(main_title)
    fr_text_embedding = np.array([0]*768).astype(np.float32)
    nl_text_embedding = np.array([0]*768).astype(np.float32)

    return main_title_embedding,fr_text_embedding,nl_text_embedding

def remove_extra_spaces(s):
    return re.sub(r"\s+", " ", s).strip()


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
    elif text == "Avis Du Conseil D'Etat":
        return "Opinion of the Council of State"
    elif text == "Rapport Complementaire":
        return "Complementary Report"
    elif text == "Avis":
        return "Opinion"
    else:
        return "Other"
    

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
            "Date"
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

<<<<<<< HEAD
        data_list.append(
            {
                "title": text,
                "document_page_url": ROOT_URL,
                "document_number": dossier_id,
                "fr_text": "",
                "date": dossier_date_formatted,
                "link_to_document": pdf_link,
                "pdf id": pdf_link_element,
                "keywords": "",
                "source": "Documents Parlementaires Récents",
                "commissionchambre": "",
                "nl_text": "",
                "stakeholders": "",
                "status": "",
                "title_embedding": [],  # preprocess -> not for engineers
                "fr_text_embedding": [],  # preprocess -> not for engineers
                "nl_text_embedding": [],  # preprocess -> not for engineers
                "topic": "",  # preprocess -> not for engineers
                "policy_level": "",  # preprocess -> not for engineers
                "type": "",  # preprocess -> not for engineers
                "issue": "",  # preprocess -> not for engineers
                "reference": "",  # preprocess -> not for engineers
                "maindocuments": "",
                "typededocument": dossier_type_of_document_formatted,
                "descripteurEurovocprincipal": "",
                "descripteursEurovoc": "",
                "seancepleinierechambre": "",
                "compťtence": "",
                "1_commissionchambre": "",
                "2_commissionchambre": "",
                "1_seancepleinierechambre": "",
                "2_seancepleinierechambre": "",
            }
        )
    return data_list
=======
        data = {"fr_title": dossier_type_of_document_formatted.title(),
            "document_number": f"{dossier_id}/{pdf_link_element}",
            "date": dossier_date_formatted,
            "document_page_url": ROOT_URL,
            "fr_main_title": text,
            "link_to_document": pdf_link,
            "fr_source": "Documents Parlementaires Récents",
            "fr_type": get_type(dossier_type_of_document_formatted.title())}
    
        existing_document = col.find_one({"document_number": data["document_number"],"fr_source":"Documents Parlementaires Récents"})
>>>>>>> 1a97400160b5cd1ddce445332f00427da7dbe180

        if existing_document:
            print("Document with the same doc_number already exists.")
        else:
            main_title_embedding, fr_text_embedding, nl_text_embedding  = embed(main_title=data["fr_main_title"], model=model)
            data["fr_title_embedding"] = (main_title_embedding.tolist())
            data["fr_text_embedding"] = (fr_text_embedding.tolist())
            data["nl_text_embedding"] = (nl_text_embedding.tolist())

            col.insert_one(data)

def save_file(data):
    with open("data/new_documents_parlementaires_recents_fr.json", "w") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


def main():
    print("Starting scrapping...")

    with requests.Session() as session:
        data = get_all_data(ROOT_URL, session)

    # save_file(data)
    print("Finished")


if __name__ == "__main__":
    main()

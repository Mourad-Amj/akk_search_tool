import requests
from bs4 import BeautifulSoup as bs
import re
import time
import pandas as pd
import numpy as np
import pymongo
import certifi
import os
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer, util

# import torch
start_time = time.perf_counter()

load_dotenv()
connection = os.getenv("MONGODB_URI")
client = pymongo.MongoClient(connection, tlsCAFile=certifi.where())
db = client["akkanto_db"]
col = db["commissions_compte_rendu_integral"]

# pre-processing functions

committees_dico = {
    "Commission Affaires sociales, Emploi et Pensions": "Social Affairs, Employment and Pensions Committee",
    "Commission Constitution et Renouveau institutionnel": "Constitution and Institutional Renewal Commission",
    "Commission Défense nationale": "National Defense Committee",
    "Commission Economie, Protection des consommateurs et Agenda numérique": "Economy, Consumer Protection and Digital Agenda Committee",
    "Commission Energie, Environnement et Climat": "Energy, Environment and Climate Committee",
    "Commission Finances et Budget": "Finance and Budget Committee",
    "Commission Intérieur, Sécurité, Migration et Matières administratives": "Internal, Security, Migration and Administrative Matters Committee",
    "Commission Justice": "Justice Committee",
    "Commission Mobilité, Entreprises publiques et Institutions fédérales": "Mobility, Public Enterprises and Federal Institutions Committee",
    "Commission Relations extérieures": "External Relations Committee",
    "Commission Santé et Egalité des chances": "Health and Equal Opportunities Commission",
}


def get_policylevel(source, commissionchambre):
    if "doucement parlementaire" not in source.lower():
        for key in committees_dico:
            commission_list = [
                word for word in commissionchambre.split(" ") if word[0].isupper()
            ]
            if commission_list[1] in key:
                policylevel = f"Federal Parliament ({committees_dico[key]})"
                return policylevel


def get_type():
    type = "Oral Question"
    return type


def get_issue(main_text):
    sample = main_text.split('"')
    output = f'"{sample[-2]}"{sample[-1]}'
    return output


members = pd.read_csv("src/Belgian_Parliament_Members.csv")


def party_name(stakeholder):
    for index, value in members["Representative"].items():
        # print(type(value))
        if value.lower() in stakeholder.lower():
            stakeholder_final = f"{members.loc[index, 'Party']}"
            return stakeholder_final
        else:
            continue


def get_stakeholders(stakeholder):
    party_name_politician = party_name(stakeholder)
    if party_name_politician == None:
        return stakeholder
    else:
        stakeholder_final = f"{stakeholder} ({party_name(stakeholder)})"
        return stakeholder_final


embedder = SentenceTransformer("sentence-transformers/LaBSE")


def compute_embedding(doc):
    # tag = embedding
    if doc == "":
        return np.array([0] * 768).astype(np.float32).tolist()
    else:
        embedded_text = embedder.encode(doc, convert_to_tensor=False).tolist()
        return embedded_text


# scraping


def date_convert(date: str) -> str:
    date_dict = {
        "janvier": "01",
        "février": "02",
        "mars": "03",
        "avril": "04",
        "mai": "05",
        "juin": "06",
        "juillet": "07",
        "août": "08",
        "septembre": "09",
        "octobre": "10",
        "novembre": "11",
        "décembre": "12",
    }
    date_list = date.split()
    return date_list[0] + "/" + date_dict[date_list[1]] + "/" + date_list[2]


main_url = "https://www.lachambre.be/kvvcr/showpage.cfm?section=/cricra&language=fr&cfm=dcricra.cfm?type=comm&cricra=cri&count=all"


main_response = requests.get(main_url)
soup = bs(main_response.content, "html.parser")


rows = soup.find_all("tr", valign="top")
for row in rows:
    new_elements = row.findChildren()
    pdf_link = "https://www.lachambre.be" + new_elements[0].find("a")["href"]
    name = new_elements[0].text.strip()
    unpro_date = new_elements[5].text.strip()
    try:
        date = date_convert(unpro_date)
    except:
        print("problem with source date format.")
    main_title = "Compte rendu intégral - Commissions - Législature 55"

    if new_elements[8].name == "a":
        pda_link = "https://www.lachambre.be" + new_elements[8]["href"]
        commission = new_elements[12].text.strip()
        version = new_elements[11].text.strip()
    else:
        pda_link = ""
        commission = new_elements[10].text.strip()
        version = new_elements[9].text.strip()

    if new_elements[9].name == "a":
        text_link = "https://www.lachambre.be" + new_elements[9]["href"]
    else:
        text_link = ""

    try:
        question_response = requests.get(text_link)
    except:
        print("Not a valid url.")

    question_soup = bs(question_response.content, "html.parser")

    for h2_tag in question_soup.find_all(
        "h2"
    ):  # remmeber to reaplce with question_soup
        text = h2_tag.text.strip()
        question_code_flag = 0
        if (
            re.compile(r"\(\d{8}\w\)").search(text) != None
        ):  # verify that the question title text has the document code, example (55036821C)
            if (
                question_code_flag == 2
            ):  # condition to stop if two different question titles have the same document code
                question_code_flag = 0
                continue
            else:
                question_code = text.split()[-1]
                question_code_flag = 1
                # Sometimes the first question has FR and the second NL and vice versa, this is a check for it.

                try:
                    if h2_tag.span["lang"] == "FR":
                        question_FR = " ".join(text.split())
                        start_with = text.split("à")[0]
                        end_with = text.split("à")[1]
                        politician_adressed = end_with.split("(")[0].strip()
                        if "Question de" in start_with:
                            politician_asking = start_with.split("de")[1].strip()
                        elif "-" in start_with:
                            politician_asking = " ".join(start_with.split()[1:])
                    elif h2_tag.span["lang"] == "NL":
                        question_NL = " ".join(text.split())
                        start_with = text.split("aan")[0]
                        end_with = text.split("aan")[1]
                        politician_adressed = end_with.split("(")[0].strip()
                        if "Vraag van" in start_with:
                            politician_asking = start_with.split("Vraag van")[1].strip()
                        elif "-" in start_with:
                            politician_asking = " ".join(start_with.split()[1:])
                except:
                    print("problem with span lang attribute.")
                    print(h2_tag.span)

                for next_h2_tag in h2_tag.find_next_siblings("h2"):
                    next_text = next_h2_tag.text.strip()
                    if question_code in next_text:
                        question_code_flag = 2
                        try:
                            if next_h2_tag.span["lang"] == "FR":
                                question_FR = " ".join(next_text.split())
                            elif next_h2_tag.span["lang"] == "NL":
                                question_NL = " ".join(next_text.split())
                        except:
                            print("problem with span lang attribute.")
                            print(h2_tag.span)

                        existing_document = col.find_one(
                            {"fr_main_title": get_issue(question_FR)}
                        )
                        if existing_document:
                            print("A document with this question already exists.")
                            print(get_issue(question_FR))
                            print()
                        else:
                            document_dict = {}
                            document_dict["title"] = main_title
                            document_dict["document_number"] = name
                            document_dict["date"] = date
                            document_dict["document_page_url"] = main_url
                            document_dict["fr_main_title"] = get_issue(
                                question_FR
                            )  # should be later used to display the issue
                            document_dict["nl_main_title"] = get_issue(question_NL)
                            document_dict["link_to_document"] = pdf_link
                            document_dict["keywords"] = ""
                            document_dict[
                                "fr_source"
                            ] = "Commissions Compte rendu intégral"
                            document_dict["commissionchambre"] = commission
                            document_dict["fr_text"] = ""
                            document_dict["nl_text"] = ""
                            document_dict["fr_stakeholders"] = (
                                get_stakeholders(politician_asking)
                                + ", "
                                + get_stakeholders(politician_adressed)
                            )
                            document_dict["status"] = ""
                            document_dict["title_embedding"] = compute_embedding(
                                main_title
                            )
                            document_dict["fr_text_embedding"] = compute_embedding("")
                            document_dict["nl_text_embedding"] = compute_embedding("")
                            document_dict["fr_title_embedding"] = compute_embedding(
                                question_FR
                            )
                            document_dict["nl_title_embedding"]: compute_embedding(
                                question_NL
                            )
                            document_dict["topic"] = ""
                            document_dict["policy_level"] = get_policylevel(
                                main_title, commission
                            )
                            document_dict["type"] = get_type()

                            print("Adding document with question : ")
                            print(document_dict["fr_main_title"])
                            print()
                            col.insert_one(document_dict)
                        break

end_time = time.perf_counter()
print(round(end_time - start_time, 2), "seconds")

import requests
from bs4 import BeautifulSoup as bs
import re
import json
import time
import pandas as pd
import numpy as np
import pymongo
import certifi
import os
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer, util

<<<<<<< HEAD

def get_text(text_link, session):
    french_text = ""
    dutch_text = ""
    try:
        response = session.get(text_link)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")

            span_elements = soup.find_all(
                "span", lang="FR"
            )  # Find all <span> elements with lang="FR"

            for span in span_elements:
                if span.find_parent("table") is None and span.find_parent(
                    "p", attrs={"NormalFR"}
                ):  # Check if the span is not within a table
                    # print(span.get_text())
                    french_text += span.get_text()

            span_elements = soup.find_all(
                "span", lang="NL-BE"
            )  # Find all <span> elements with lang="FR"

            for span in span_elements:
                if span.find_parent("table") is None and span.find_parent(
                    "p", attrs={"NormalNL"}
                ):  # Check if the span is not within a table
                    # print(span.get_text())
                    dutch_text += span.get_text()
=======
start_time = time.perf_counter()

load_dotenv()
connection = os.getenv("MONGODB_URI")
client = pymongo.MongoClient(connection, tlsCAFile=certifi.where())
db = client["akkanto_db"]
col = db["seances_plenieres_compte_rendu_integral"]

>>>>>>> 1a97400160b5cd1ddce445332f00427da7dbe180

# pre-processing functions
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
<<<<<<< HEAD
            print("Failed to fetch the file")
    except requests.exceptions.RequestException:
        print("Error fetching the file")

    return french_text, dutch_text


=======
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


>>>>>>> 1a97400160b5cd1ddce445332f00427da7dbe180
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
<<<<<<< HEAD


main_url = "https://www.lachambre.be/kvvcr/showpage.cfm?section=/cricra&language=fr&cfm=dcricra.cfm?type=comm&cricra=cri&count=all"

session = requests.Session()
response = session.get(main_url)
html_content = response.text
soup = BeautifulSoup(html_content, "html.parser")
link_list = []
data_dict = {}
rows = soup.find_all("tr", valign="top")
=======
>>>>>>> 1a97400160b5cd1ddce445332f00427da7dbe180


main_url = "https://www.lachambre.be/kvvcr/showpage.cfm?section=/cricra&language=fr&cfm=dcricra.cfm?type=plen&cricra=cri&count=all"

main_response = requests.get(main_url)
soup = bs(main_response.content, "html.parser")


rows = soup.find_all("tr", valign="top")
for row in rows:
<<<<<<< HEAD
    row_elements = row.findChildren()
    pdf_link = "https://www.lachambre.be" + row_elements[0].find("a")["href"]
    name = row_elements[0].text.strip()
    unpro_date = row_elements[5].text.strip()
    date = date_convert(unpro_date)

    pda_link = "https://www.lachambre.be" + row_elements[8]["href"]
    text_link = "https://www.lachambre.be" + row_elements[9]["href"]
    version = row_elements[11].text.strip()
    french_text, dutch_text = get_text(text_link, session)

    data_dict = {
        "First Title": "Séances Plénières",
        "Main Title": "Compte rendu intégral - Séance plénière- Législature 55",
        "Document_name": name,
        "Date": date,
        "Document_pdf_link": pdf_link,
        "Document_pda_link": pda_link,
        "Document_text_link": text_link,
        "Version": version,
        "French_text": french_text,
        "Dutch_text": dutch_text,
    }

    link_list.append(data_dict)
"""headers = ["First Title","Main Title","Document_name","Date","Document_pdf_link","Document_pda_link","Document_text_link","Version","French_text","Dutch_text"]
with open("Compte_rendu_intégral.csv", "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=headers)
        writer.writeheader()
        writer.writerows(link_list)"""

json_filename = "data/seances_plenieres_compte_rendu_integral.json"
with open(json_filename, mode="w", encoding="utf-8") as json_file:
    json.dump(link_list, json_file, indent=4, ensure_ascii=False)

    print(f"Extracted data saved to '{json_filename}'")
=======
    new_elements = row.findChildren()
    pdf_link = "https://www.lachambre.be" + new_elements[0].find("a")["href"]
    name = new_elements[0].text.strip()
    unpro_date = new_elements[5].text.strip()
    try:
        date = date_convert(unpro_date)
    except:
        print("problem with source date format.")
    main_title = "Compte rendu intégral - Séance plénière- Législature 55"

    pda_link = "https://www.lachambre.be" + new_elements[8]["href"]
    text_link = "https://www.lachambre.be" + new_elements[9]["href"]
    version = new_elements[11].text.strip()

    try:
        question_response = requests.get(text_link)

    except:
        print("Not a valid url.")
    question_soup = bs(question_response.content, "html.parser")
    for h2_tag in question_soup.find_all("h2"):
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
                        start_with = text.split("à")[0].strip()
                        end_with = text.split("à")[1].strip()
                        politician_adressed = end_with.split("(")[0].strip()
                        if "Question de" in start_with:
                            politician_asking = start_with.split("Question de")[
                                1
                            ].strip()
                        elif "-" in start_with:
                            politician_asking = " ".join(start_with.split()[1:])

                    elif h2_tag.span["lang"] == "NL":
                        question_NL = " ".join(text.split())
                        start_with = text.split("aan")[0].strip()
                        end_with = text.split("aan")[1].strip()
                        politician_adressed = end_with.split("(")[0].strip()
                        if "Vraag van" in start_with:
                            politician_asking = start_with.split("Vraag van")[1].strip()
                        elif "-" in start_with:
                            politician_asking = " ".join(start_with.split()[1:])

                except:
                    print("problem with span lang attribute.")
               
                
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
                            ] = "Séances Plénières Compte rendu intégral"
                            document_dict["commissionchambre"] = "Plenary Session"
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
                            document_dict["nl_title_embedding"] = compute_embedding(
                                question_NL
                            )
                            document_dict["topic"] = ""
                            document_dict[
                                "policy_level"
                            ] = "Federal Parliament (Plenary Session)"
                            document_dict["type"] = get_type()

                            print("Adding document with question : ")
                            print(document_dict["fr_main_title"])
                            print()
                            col.insert_one(document_dict)
                        break
end_time = time.perf_counter()
print(round(end_time - start_time, 2), "seconds")
>>>>>>> 1a97400160b5cd1ddce445332f00427da7dbe180

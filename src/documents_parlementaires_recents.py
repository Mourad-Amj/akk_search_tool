import requests
from bs4 import BeautifulSoup as bs
import json
import tqdm
import re

ROOT_URL = "https://www.lachambre.be/kvvcr/showpage.cfm?section=/flwb/recent&language=fr&cfm=/site/wwwcfm/flwb/rapweekweekly.cfm?week=4"
LINK_PREFIX = "https://www.lachambre.be/kvvcr/"


def get_links(url, session):
    response = requests.get(url, session)
    soup = bs(response.text, "html.parser")
    links = soup.select("a[href*=dossierID]")

    for link in links:
        if link.findChild("img"):
            continue

        href_value = link.attrs.get("href")
        final_link = f"{LINK_PREFIX}{href_value}"

        yield final_link


def get_all_data(link, session):
    data = {}

    response2 = session.get(link)
    soup2 = bs(response2.text, "html.parser")

    data["document_page_url"] = link

    finding_document_number = link.split("=")[7]
    data["document_number"] = finding_document_number

    finding_first_title = soup2.find("center")
    first_title = finding_first_title.text.strip()
    data["title"] = first_title

    finding_main_title = soup2.find_all("center")
    main_title = finding_main_title[1].text.strip()
    data["main_title"] = main_title

    finding_date = soup2.find_all("td")
    regex = r"\d{1,2}/\d{1,2}/\d{1,4}"
    for i, all_dates in enumerate(finding_date):
        dates = all_dates.text.strip()
        if match := re.search(regex, dates, re.IGNORECASE):
            data["date"] = match[0]

    finding_url_pdf = soup2.select("a[href*=lachambre]")
    url_pdf_cleansing = finding_url_pdf[0]
    url_pdf = url_pdf_cleansing.attrs.get("href")
    data["link_to_document"] = url_pdf

    type_of_document = []
    finding_type_de_document = soup2.select("td", {"class": "td0x"})
    for i, all_documents in enumerate(finding_type_de_document):
        if all_documents.text.strip() == "Type de document":
            type_of_document.append(
                " ".join(finding_type_de_document[i + 1].text.split(", "))
            )
    data["typededocument"] = " ".join(type_of_document[0].split(" ")[1:])

    finding_auteurs = soup2.find_all("td", class_="td0x")
    for i, all_auteurs in enumerate(finding_auteurs):
        if "(AUTEUR)" in all_auteurs.text.strip():
            auteurs = finding_auteurs[i].text.replace("(AUTEUR)", "").strip()
            data["stakeholders"] = auteurs
            break

    finding_commission = soup2.find_all("td", class_="td0x")
    for i, commissions in enumerate(finding_commission):
        if "(PUBLIC)" in commissions.text.strip():
            all_commissions = (
                commissions.text.strip(", ")
                .replace("PRESIDENT CHAMBRE", "")
                .split("\r")[0]
            )
            data["commissionchambre"] = all_commissions
            break

    data["source"] = "Documents Parlemantaire Récents"

    data["keywords"] = ""
    keywords_finding = soup2.find_all("td")
    for i, all_keywords in enumerate(keywords_finding):
        if all_keywords.text.strip() == "Descripteurs Eurovoc":
            keywords = keywords_finding[i + 1].text.split(", ").strip(" | ")
            data["keywords"] = keywords

    data["fr_text"] = ""
    data["nl_text"] = ""
    data["status"] = ""
    data["title_embedding"] = []  # preprocess -> not for engineers
    data["fr_text_embedding"] = []  # preprocess -> not for engineers
    data["nl_text_embedding"] = []  # preprocess -> not for engineers
    data["topic"] = ""  # preprocess -> not for engineers
    data["policy level"] = ""  # preprocess -> not for engineers
    data["type"] = ""  # preprocess -> not for engineers
    data["issue"] = ""  # preprocess -> not for engineers
    data["reference"] = ""  # preprocess -> not for engineers
    data["maindocuments"] = ""
    data["descripteurEurovocprincipal"] = ""
    data["descripteursEurovoc"] = ""
    data["seancepleinierechambre"] = ""
    data["compťtence"] = ""
    data["1_commissionchambre"] = ""
    data["2_commissionchambre"] = ""
    data["1_seancepleinierechambre"] = ""
    data["2_seancepleinierechambre"] = ""

    return data


def save_file(data):
    with open("data/Documents_parlementaires_récents.json", "w") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


def main():
    print("Starting scrapping...")
    data = []
    with requests.Session() as session:
        for link in tqdm.tqdm(get_links(ROOT_URL, session)):
            data.append(get_all_data(link, session))

    save_file(data)
    print("Finished")


if __name__ == "__main__":
    main()

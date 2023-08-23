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

    document_page_url = link
    document_number = link.split("=")[7]
    title = soup2.find("center").text.strip()
    main_title = soup2.find_all("center")[1].text.strip()

    date = ""
    finding_date = soup2.find_all("td")
    regex_date = r"\d{1,2}/\d{1,2}/\d{1,4}"
    for i, all_dates in enumerate(finding_date):
        dates = all_dates.text.strip()
        if match := re.search(regex_date, dates, re.IGNORECASE):
            date = match[0]
            break

    finding_url_pdf = soup2.select("a[href*=lachambre]")[0].attrs.get("href")

    type_of_document = []
    finding_type_de_document = soup2.select("td", {"class": "td0x"})
    for i, all_documents in enumerate(finding_type_de_document):
        if all_documents.text.strip() == "Type de document":
            type_of_document.append(
                " ".join(finding_type_de_document[i + 1].text.split(", "))
            )
            break

    stakeholders = ""
    finding_auteurs = soup2.find_all("td", class_="td0x")
    for i, all_auteurs in enumerate(finding_auteurs):
        if "(AUTEUR)" in all_auteurs.text.strip():
            auteurs = finding_auteurs[i].text.replace("(AUTEUR)", "").strip()
            stakeholders = auteurs
            break

    commisionchambre = ""
    finding_commission = soup2.find_all("td", class_="td0x")
    for i, commissions in enumerate(finding_commission):
        if "(PUBLIC)" in commissions.text.strip():
            all_commissions = (
                commissions.text.strip(", ")
                .replace("PRESIDENT CHAMBRE", "")
                .split("\r")[0]
            )
            commisionchambre = all_commissions
            break

    keywords = ""
    keywords_finding = soup2.find_all("td")
    for i, all_keywords in enumerate(keywords_finding):
        if all_keywords.text.strip() == "Descripteurs Eurovoc":
            keywords = keywords_finding[i + 1].text.split(", ")
            break

    data = {
        "title": title,
        "document_number": document_number,
        "date": date,
        "document_page_url": document_page_url,
        "main_title": main_title,
        "link_to_document": finding_url_pdf,
        "keywords": keywords,
        "source": "Documents Parlemantaire Récents",
        "commissionchambre": commisionchambre,
        "fr_text": "",
        "nl_text": "",
        "stakeholders": stakeholders,
        "status": "",
        "title_embedding": [],
        "fr_text_embedding": [],
        "nl_text_embedding": [],
        "topic": "",
        "policy_level": "",
        "type": "",
        "issue": "",
        "reference": "",
        "maindocuments": "",
        "typededocument": " ".join(type_of_document[0].split(" ")[1:]),
        "descripteurEurovocprincipal": "",
        "descripteursEurovoc": "",
        "seancepleinierechambre": "",
        "compťtence": "",
        "1_commissionchambre": "",
        "2_commissionchambre": "",
        "1_seancepleinierechambre": "",
        "2_seancepleinierechambre": "",
    }

    return data


def save_file(data):
    with open("data/documents_parlementaires_recents.json", "w") as f:
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

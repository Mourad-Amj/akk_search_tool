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
    # print(link)

    data["Page's main url"] = link

    finding_document_number = link.split("=")[7]
    data["Document Number"] = finding_document_number

    finding_first_title = soup2.find("center")
    first_title = finding_first_title.text.strip()
    data["First title"] = first_title

    finding_main_title = soup2.find_all("center")
    main_title = finding_main_title[1].text.strip()
    data["Main title"] = main_title

    finding_date = soup2.find_all("td")
    regex = r"\d{1,2}/\d{1,2}/\d{1,4}"
    for i, all_dates in enumerate(finding_date):
        dates = all_dates.text.strip()
        if match := re.search(regex, dates, re.IGNORECASE):
            date = match
    data["Date de dépôt"] = date

    finding_url_pdf = soup2.select("a[href*=lachambre]")
    url_pdf_cleansing = finding_url_pdf[0]
    url_pdf = url_pdf_cleansing.attrs.get("href")
    data["URL of pdf"] = url_pdf

    finding_type_de_document = soup2.find_all("td", attrs="td0x")
    type_de_document_found = finding_type_de_document[6].text.split()[3:6]
    type_de_document_clean = " ".join(type_de_document_found)
    data["Type"] = type_de_document_clean

    auteurs = []
    finding_auteurs = soup2.select("td")
    for i, all_auteurs in enumerate(finding_auteurs):
        if all_auteurs.text.strip() == "Auteur(s)":
            found_auteurs = all_auteurs.text.split()
            auteurs = finding_auteurs[i + 1].text.split(", ")
    find_auteurs = " ".join(auteurs).replace("(AUTEUR)", "")
    data["Stakeholders"] = find_auteurs

    finding_commission = soup2.select("td")
    for i, commission in enumerate(finding_commission):
        if "(PUBLIC)" in commission.text.strip():
            all_commissions = commission.text.strip(", ").split("\r")[0].strip()
            if all_commissions:
                data["Commissions"] = all_commissions

    return data


def save_file(data):
    with open("data/Documents_parlementaires_récents.json", "w") as f:
        json.dump(data, f)


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

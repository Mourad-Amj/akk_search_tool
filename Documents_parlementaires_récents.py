import requests
from bs4 import BeautifulSoup as bs
import json
import tqdm

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

    document_number = soup2.find("center")
    document = document_number.text.strip()
    data["documents"] = document

    finding_title = soup2.find_all("center")
    title = finding_title[1].text.strip()
    data["title"] = title

    finding_date = soup2.find_all("td", attrs="td0x")
    date = finding_date[3].text.strip()
    data["date"] = date

    finding_pdf = soup2.select("a[href*=lachambre]")
    pdf_cleansing = finding_pdf[0]
    pdf = pdf_cleansing.attrs.get("href")
    data["pdf"] = pdf

    return data


def save_file(data):
    with open("data/full_data.json", "w") as file:
        json.dump(data, file)


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

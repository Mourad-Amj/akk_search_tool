"""
Scrape the table data including links to pdfs of documents for
all documents of the 'Apercu Complet' page of the lachambre.be site
"""

import requests
import json
from bs4 import BeautifulSoup as bs


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
for group_document_url in group_document_urls:
    url_soup = get_soup(group_document_url)
    table = url_soup.find("table")
    document_links = table.find_all("a")
    documents = [base_url + link["href"] for link in document_links]
    for index, document in enumerate(documents, start=1):
        print(f"Adding document data {index} of {len(documents)} ...")
        document_soup = get_soup(document)
        document_dict = {}
        section = document_soup.find("div", attrs={"id": "Story"})
        document_dict["first_title"] = section.find("h3").text.strip()
        document_dict["document_number"] = document_dict["first_title"][-4:]
        document_dict["document_page_url"] = document
        document_dict["main_title"] = section.find("h4").text.strip()
        document_table = section.find("table")
        for rows in document_table.select("tr"):
            cells = rows.find_all("td", recursive=False)
            for cell in cells:
                if cell.find("table"):
                    cell.decompose()
                    continue
                header = "".join(cells[0].text.split())
                content = "".join(cells[1].text.split())
            if header == "DocumentChambre":
                try:
                    document_dict[header] = rows.find("a").get("href")
                except:
                    document_dict[header] = content
            else:
                document_dict[header] = content
        document_list.append(document_dict)

with open("data/apercu_complet.json", "w") as fout:
    json.dump(document_list, fout)

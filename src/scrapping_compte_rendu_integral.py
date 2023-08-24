import requests
from bs4 import BeautifulSoup
import pandas as pd
import lxml
import csv

main_url = "https://www.lachambre.be/kvvcr/showpage.cfm?section=/cricra&language=fr&cfm=dcricra.cfm?type=plen&cricra=cri&count=all"
session = requests.Session()
response = session.get(main_url)
html_content = response.text
soup = BeautifulSoup(html_content, "html.parser")

link_list = []
data_dict = {}
rows = soup.find_all("tr", valign="top")
for row in rows:
    row_elements = row.findChildren()
    pdf_link = "https://www.lachambre.be" + row_elements[0].find("a")["href"]
    name = row_elements[0].text.strip()
    date = row_elements[5].text.strip()
    pda_link = "https://www.lachambre.be" + row_elements[8]["href"]
    text_link = "https://www.lachambre.be" + row_elements[9]["href"]

    data_dict = {
        "Document_name": name,
        "Date": date,
        "Document_pdf_link": pdf_link,
        "Document_pda_link": pda_link,
        "Document_text_link": text_link,
    }

    link_list.append(data_dict)
headers = [
    "Document_name",
    "Date",
    "Document_pdf_link",
    "Document_pda_link",
    "Document_text_link",
]
with open(
    "data/compte_rendu_integral.csv", "w", newline="", encoding="utf-8"
) as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=headers)
    writer.writeheader()
    writer.writerows(link_list)

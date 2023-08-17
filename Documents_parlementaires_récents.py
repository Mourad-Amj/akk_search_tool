import requests
from bs4 import BeautifulSoup as bs
import json

ROOT_URL = "https://www.lachambre.be/kvvcr/showpage.cfm?section=/flwb/recent&language=fr&cfm=/site/wwwcfm/flwb/rapweekweekly.cfm?week=4"
LINK_PREFIX = "https://www.lachambre.be/kvvcr/"

response = requests.get(ROOT_URL)
soup = bs(response.text, "html.parser")


links = soup.select("a[href*=dossierID]")

urls_list = []

for link in links:
    if link.findChild("img"):
        continue

    href_value = link.attrs.get("href")

    final_url = f"{LINK_PREFIX}{href_value}"
    urls_list.append(final_url)


merci_maxim = []
for url in urls_list:
    response2 = requests.get(url)
    soup2 = bs(response2.text, "html.parser")

    document_number = soup2.find("center")
    document = document_number.text.strip()

    finding_title = soup2.find_all("center")
    title = finding_title[1].text.strip()

    finding_date = soup2.find_all("td", attrs="td0x")
    date = finding_date[2].text.strip()

    finding_pdf = soup2.select("a[href*=lachambre]")
    pdf_cleansing = finding_pdf[0]
    pdf = pdf_cleansing.attrs.get("href")

    hello = document + ", " + title + ", " + date + ", " + pdf

    merci_maxim.append(hello)

print(merci_maxim)

with open("test.json", "w") as file:
    json.dump(merci_maxim, file)

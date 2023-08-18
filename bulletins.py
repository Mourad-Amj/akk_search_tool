import requests
from bs4 import BeautifulSoup as bs
import re
import pandas as pd

page_numbers = range(48, 56)
ROOT_URL = f"https://www.lachambre.be/kvvcr/showpage.cfm?&language=fr&cfm=/site/wwwcfm/qrva/qrvaList.cfm?legislat={page_numbers}"
LINK_PREFIX = "https://www.lachambre.be"


merci_paull = []

for page_number in page_numbers:
    url = ROOT_URL.format(page_number=page_number)
    response = requests.get(url)
    soup = bs(response.text, "html.parser")

    pdf_links = ""
    for link in soup.find_all('a', href=True):
        if link['href'].endswith('pdf') and link['href'].startswith("/QRVA"):
            full_link = LINK_PREFIX + link['href']
            if full_link not in pdf_links:
                pdf_links += full_link + "\n"


        bulletins = soup.select("a[href*=QRVA]")
        for bulletin in bulletins:
            bulletins = bulletin.text.strip()

            finding_date = soup.find_all("td")
            for date in finding_date:
                if "/" in date.text.strip():
                    dates = date.text.strip()

    hello = pdf_links + ", " + bulletins + ", " + dates + ","

    merci_paull.append(hello)

print(merci_paull)
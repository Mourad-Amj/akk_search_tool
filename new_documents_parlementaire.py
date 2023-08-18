import requests
from bs4 import BeautifulSoup as bs
import json
import tqdm
import re

ROOT_URL = "https://www.lachambre.be/kvvcr/showpage.cfm?section=/flwb/recent&language=fr&cfm=/site/wwwcfm/flwb/rapweekweekly.cfm?week=4"
LINK_PREFIX = "https://www.lachambre.be/kvvcr/"
PDF_PREFIX = "https://www.lachambre.be"


def remove_extra_spaces(s):
    return re.sub(r"\s+", " ", s).strip()


def get_all_data(link, session):
    data = {}
    regex = r"\d{1,2}/\d{1,2}/\d{1,4}"

    response = session.get(link)

    with open("soup_test_1.html", "w") as f:
        f.write(response.text)
    soup = bs(response.text, "html.parser")

    finding_element = soup.find_all("div", class_="linklist_1")
    print(f"found {len(finding_element)} linklist_1")
    for element in finding_element:
        dossier_id_element = element.find("a")
        dossier_id = dossier_id_element.text
        print("dossier id: ", dossier_id)
        try:
            text_div_element = (
                dossier_id_element.parent.parent.find_next_sibling().find("div")
            )
        except AttributeError:
            # print(f"skip for {dossier_id}")
            continue
        # print("text div element: ", remove_extra_spaces(text_div_element.text))

        dossier_content_div_text = remove_extra_spaces(text_div_element.text).split(
            "Date"
        )
        dossier_text = dossier_content_div_text[0]
        dossier_date = dossier_content_div_text[1]

        dossier_date_formatted = None
        match = re.search(regex, dossier_date, re.IGNORECASE)
        if match:
            dossier_date_formatted = match[0]

        pdf_link = None
        pdf_link_element = text_div_element.find("a")
        if pdf_link_element["href"].startswith("/site/wwwcfm/flwb/flwbcheckpdf"):
            pdf_link = PDF_PREFIX + pdf_link_element["href"]

        data[dossier_id] = {
            "text": dossier_text,
            "date": dossier_date_formatted,
            "pdf_link": pdf_link,
        }

        print("text: ", dossier_text)
        print("date: ", dossier_date_formatted)
        print("pdf: ", pdf_link)
    return data


def save_file(data):
    with open("data/New_Documents_Parlementaires_Récents.json", "w") as f:
        json.dump(data, f)


def main():
    print("Starting scrapping...")

    with requests.Session() as session:
        data = get_all_data(ROOT_URL, session)

    save_file(data)
    print("Finished")


if __name__ == "__main__":
    main()

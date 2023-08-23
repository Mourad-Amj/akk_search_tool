import requests
from bs4 import BeautifulSoup as bs
import json
from tqdm import tqdm
import ssl
ssl._create_default_https_context = ssl._create_unverified_context

ROOT_URL = "https://www.lachambre.be/kvvcr/showpage.cfm?&language=fr&cfm=/site/wwwcfm/qrva/qrvaList.cfm?legislat=55"
LINK_PREFIX = "https://www.lachambre.be"

def clean_unicode(text):
    return text.encode('utf-8').decode('latin-1')

def scrape_data(session, main_link):
    data_list = []
    main_response = session.get(main_link)
    main_soup = bs(main_response.text, "html.parser")
    links = main_soup.find_all("div", class_=["linklist_0", "linklist_1"])
    
    for link in tqdm(links, desc="Scraping links"):
        final_link = link.find("a")
        if final_link is not None:
            href = final_link.get("href")
            full_link = LINK_PREFIX + "/kvvcr/" + href
            data_dict = {}
            response = session.get(full_link)
            soup = bs(response.text, "html.parser")

            title = clean_unicode(soup.find("h1").text.strip())

            data_dict["page_url"] = full_link
            data_dict["title"] = title
            document_table = soup.find("table")
            if document_table is not None:
                for rows in document_table.select("tr"):
                    cells = rows.find_all("td", recursive=False)
                    header = " ".join(cells[0].text.split())
                    if not header and not cells[1].text.strip():
                        continue

                    for cell in cells:
                        if cell.find("table"):
                            cell.decompose()
                            continue
                        content = " ".join(cell.text.split())

                    if header == "Publication question" or header == "Publication réponse":
                        try:
                            link = rows.find("a").get("href")
                            full_link = "https://www.lachambre.be" + link
                            data_dict[header] = full_link
                        except:
                            data_dict[header] = content
                    else:
                        data_dict[header] = content

                data_list.append(data_dict)

            else:
                print("No table")
    
    return data_list

def formatted_data(datas):
    output_data = []
    
    for data in datas:
        new_data = {
            "title": data["Question"],
            "document_number": data["title"],
            "date": data["Date de délai"],
            "document_page_url": data["page_url"],
            "main_title": data["title"],
            "link_to_document": data.get("Publication question", "") or data.get("Publication réponse", ""),
            "keywords": data.get("Mots-clés libres", ""),
            "source": "",
            "commissionchambre": data["Département"],
            "fr_text": data.get("Réponse", ""),
            "nl_text": "",
            "stakeholders": data["Auteur"],
            "status": data["Statut question"],
            "title_embedding": [],
            "fr_text_embedding": [],
            "nl_text_embedding": [],
            "topic": "",
            "policy level": "",
            "type": "",
            "issue": "",
            "reference": "",
            "maindocuments": "",
            "typededocument": "",
            "descripteurEurovocprincipal": data.get("Desc. Eurovoc principal", ""),
            "descripteursEurovoc": data.get("Descripteurs Eurovoc", ""),
            "seancepleinierechambre": "",
            "compétence": "",
            "1_commissionchambre": "",
            "2_commissionchambre": "",
            "1_seancepleinierechambre": "",
            "2_seancepleinierechambre": "",
        }
        output_data.append(new_data)
    
    return output_data

def main():
    session = requests.Session()
    response = session.get(ROOT_URL)
    soup = bs(response.text, "html.parser")

    contenu_links = []   
    contenu_link = soup.find_all("a")
    for link in contenu_link:
        href = link.get("href")
        if href.startswith("showpage.cfm?&language=fr&cfm=/site/wwwcfm/qrva/qrvatoc.cfm"):
            full_link = LINK_PREFIX + "/kvvcr/" + href
            if full_link not in contenu_links:
                contenu_links.append(full_link)
    
    all_data = []
    for main_link in contenu_links:
        data = scrape_data(session, main_link)
        all_data.extend(data)

    formatted_json = formatted_data(all_data)
    
    with open("data/bulletin2222.json", "w", encoding="utf-8") as f:
        json.dump(formatted_json, f, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    main()
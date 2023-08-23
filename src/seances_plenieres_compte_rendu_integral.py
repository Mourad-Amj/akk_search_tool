import requests
from bs4 import BeautifulSoup
import pandas as pd
import csv
import pymongo
import json

def get_text(text_link,session):
    french_text = ""
    dutch_text = ""
    try:
        response = session.get(text_link)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            span_elements = soup.find_all('span', lang='FR')  # Find all <span> elements with lang="FR"

            for span in span_elements:
                if span.find_parent('table') is None and span.find_parent('p', attrs={"NormalFR"}):  # Check if the span is not within a table
                    #print(span.get_text())
                    french_text += span.get_text()
            
            span_elements = soup.find_all('span', lang='NL-BE')  # Find all <span> elements with lang="FR"

            for span in span_elements:
                if span.find_parent('table') is None and span.find_parent('p', attrs={"NormalNL"}):  # Check if the span is not within a table
                    #print(span.get_text())
                    dutch_text += span.get_text()

        else:
            print("Failed to fetch the file")
    except requests.exceptions.RequestException:
        print("Error fetching the file")

    return french_text,dutch_text
     


def date_convert(date:str)-> str:
    date_dict = {'janvier' : '01','février' : '02','mars' : '03','avril' : '04','mai' : '05','juin' : '06','juillet' : '07','août': '08','septembre' :'09', 'octobre' : '10', 'novembre' :'11','décembre' :'12'
    }
    date_list = date.split()
    return date_list[0]+'/' + date_dict[date_list[1]] + "/" + date_list[2]

main_url = "https://www.lachambre.be/kvvcr/showpage.cfm?section=/cricra&language=fr&cfm=dcricra.cfm?type=comm&cricra=cri&count=all"

session = requests.Session()
response = session.get(main_url)
html_content = response.text
soup = BeautifulSoup(html_content, 'html.parser')
link_list=[]
data_dict={}
rows=soup.find_all("tr", valign="top")


for row in rows:
    row_elements = row.findChildren()
    pdf_link='https://www.lachambre.be'+ row_elements[0].find('a')['href']
    name=row_elements[0].text.strip()
    unpro_date=row_elements[5].text.strip()
    date=date_convert(unpro_date)
    

    pda_link='https://www.lachambre.be'+ row_elements[8]['href']
    text_link='https://www.lachambre.be'+ row_elements[9]['href']
    version=row_elements[11].text.strip()
    french_text,dutch_text=get_text(text_link,session)

    data_dict={
            "First Title":"Séances Plénières",
            "Main Title":"Compte rendu intégral - Séance plénière- Législature 55",
            "Document_name":name,
            "Date":date,
            "Document_pdf_link":pdf_link,
            "Document_pda_link":pda_link,
            "Document_text_link":text_link,
            "Version":version,
            "French_text":french_text,
            "Dutch_text":dutch_text
        }

    link_list.append(data_dict)
"""headers = ["First Title","Main Title","Document_name","Date","Document_pdf_link","Document_pda_link","Document_text_link","Version","French_text","Dutch_text"]
with open("Compte_rendu_intégral.csv", "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=headers)
        writer.writeheader()
        writer.writerows(link_list)"""
 
json_filename = "Séances_Plénières_Compte_rendu_intégral.json"
with open(json_filename, mode='w', encoding='utf-8') as json_file:
    json.dump(link_list, json_file, indent=4, ensure_ascii=False)
        
    print(f"Extracted data saved to '{json_filename}'")

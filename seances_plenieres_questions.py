import requests
from bs4 import BeautifulSoup as bs
import re
import json


def date_convert(date: str) -> str:
    date_dict = {
        "janvier": "01",
        "février": "02",
        "mars": "03",
        "avril": "04",
        "mai": "05",
        "juin": "06",
        "juillet": "07",
        "août": "08",
        "septembre": "09",
        "octobre": "10",
        "novembre": "11",
        "décembre": "12",
    }
    date_list = date.split()
    return date_list[0] + "/" + date_dict[date_list[1]] + "/" + date_list[2]


main_url = "https://www.lachambre.be/kvvcr/showpage.cfm?section=/cricra&language=fr&cfm=dcricra.cfm?type=plen&cricra=cri&count=all"

main_response = requests.get(main_url)
soup = bs(main_response.content, "html.parser")

questions = []
rows = soup.find_all("tr", valign="top")
for row in rows:
    new_elements = row.findChildren()
    pdf_link = "https://www.lachambre.be" + new_elements[0].find("a")["href"]
    name = new_elements[0].text.strip()
    unpro_date = new_elements[5].text.strip()
    try:
        date = date_convert(unpro_date)
    except:
        print("problem with source date format.")
    main_title = "Compte rendu intégral - Séance plénière- Législature 55"

    pda_link = "https://www.lachambre.be" + new_elements[8]["href"]
    text_link = "https://www.lachambre.be" + new_elements[9]["href"]
    version = new_elements[11].text.strip()

    try:
        question_response = requests.get(text_link)
        print(text_link)
    except:
        print("Not a valid url.")
    question_soup = bs(question_response.content, "html.parser")
    for h2_tag in question_soup.find_all("h2"):
        text = h2_tag.text.strip()
        question_code_flag = 0
        if (
            re.compile(r"\(\d{8}\w\)").search(text) != None
        ):  # verify that the question title text has the document code, example (55036821C)
            if (
                question_code_flag == 2
            ):  # condition to stop if two different question titles have the same document code
                question_code_flag = 0
                continue
            else:
                question_code = text.split()[-1]
                question_code_flag = 1
                # Sometimes the first question has FR and the second NL and vice versa, this is a check for it.

                try:
                    if h2_tag.span["lang"] == "FR":
                        question_FR = " ".join(text.split())
                        start_with = text.split("à")[0].strip()
                        end_with = text.split("à")[1].strip()
                        politician_adressed = end_with.split("(")[0].strip()
                        if "Question de" in start_with:
                            politician_asking = start_with.split("Question de")[
                                1
                            ].strip()
                        elif "-" in start_with:
                            politician_asking = " ".join(start_with.split()[1:])

                    elif h2_tag.span["lang"] == "NL":
                        question_NL = " ".join(text.split())
                        start_with = text.split("aan")[0].strip()
                        end_with = text.split("aan")[1].strip()
                        politician_adressed = end_with.split("(")[0].strip()
                        if "Vraag van" in start_with:
                            politician_asking = start_with.split("Vraag van")[1].strip()
                        elif "-" in start_with:
                            politician_asking = " ".join(start_with.split()[1:])

                except:
                    print("problem with span lang attribute.")
                    print(h2_tag.span)

                for next_h2_tag in h2_tag.find_next_siblings("h2"):
                    next_text = next_h2_tag.text.strip()
                    if question_code in next_text:
                        question_code_flag = 2
                        try:
                            if next_h2_tag.span["lang"] == "FR":
                                question_FR = " ".join(next_text.split())
                            elif next_h2_tag.span["lang"] == "NL":
                                question_NL = " ".join(next_text.split())
                        except:
                            print("problem with span lang attribute.")
                            print(h2_tag.span)
                        questions.append(
                            {
                                "title": "",
                                "document_number": name,
                                "date": date,
                                "document_page_url": main_url,
                                "main-title": main_title,
                                "link_to_document": pdf_link,
                                "keywords": "",
                                "source": main_title,
                                "commissionchambre": "",
                                "fr_text": question_FR,
                                "nl_text": question_NL,
                                "stakeholders": [
                                    politician_asking,
                                    politician_adressed,
                                ],
                                "status": "",
                                "title_embedding": [],
                                "fr_text_embedding": [],
                                "nl_text_embedding": [],
                                "topic": "",
                                "policy level": "",
                                "type": "",
                                "issue": "",
                                "reference": "",
                            }
                        )
                        break

with open("seances_plenieres_questions_test.json", "w") as fout:
    json.dump(questions, fout, ensure_ascii=False)

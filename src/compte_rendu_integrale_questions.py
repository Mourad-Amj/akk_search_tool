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


main_url = "https://www.lachambre.be/kvvcr/showpage.cfm?section=/cricra&language=fr&cfm=dcricra.cfm?type=comm&cricra=cri&count=all"


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
    main_title = "Compte rendu intégral - Commissions - Législature 55"

    if new_elements[8].name == "a":
        pda_link = "https://www.lachambre.be" + new_elements[8]["href"]
        commission = new_elements[12].text.strip()
        version = new_elements[11].text.strip()
    else:
        pda_link = ""
        commission = new_elements[10].text.strip()
        version = new_elements[9].text.strip()

    if new_elements[9].name == "a":
        text_link = "https://www.lachambre.be" + new_elements[9]["href"]
    else:
        text_link = ""

    try:
        question_response = requests.get(text_link)
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
                        start_with = text.split("à")[0]
                        end_with = text.split("à")[1]
                        politician_adressed = end_with.split("(")[0].strip()
                        if "Question de" in start_with:
                            politician_asking = start_with.split("de")[1].strip()
                        elif "-" in start_with:
                            politician_asking = " ".join(start_with.split()[1:])
                    elif h2_tag.span["lang"] == "NL":
                        question_NL = " ".join(text.split())
                        start_with = text.split("aan")[0]
                        end_with = text.split("aan")[1]
                        politician_adressed = end_with.split("(")[0].strip()
                        if "Vraag van" in start_with:
                            politician_asking = start_with.split("Vraag van")[1].strip()
                        elif "-" in start_with:
                            politician_asking = " ".join(start_with.split()[1:])
                except:
                    print("problem with span lang attribute.")
                    print(h2_tag.span)
                question_text = ""
                for p_tag in h2_tag.find_next_siblings("p"):
                    if re.compile(r"\d\d.\d\d").search(p_tag.text) and politician_asking in p_tag.text :
                        for next_p_tag in p_tag.find_next_siblings(p_tag):
                            if not re.compile(r"\d\d.\d\d").search(next_p_tag.text):
                                question_text += next_p_tag.text
                   
                print(question_text)    
                                                


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
                                "commissionchambre": commission,
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

with open("data/questions_test.json", "w") as fout:
    json.dump(questions, fout, ensure_ascii=False)




# questions = []

# test_url = "https://www.lachambre.be/doc/CCRI/html/55/ic1162x.html"
# test_response = requests.get(test_url)
# test_soup = bs(test_response.content, "html.parser")
# for h2_tag in test_soup.find_all("h2"):
#     text = h2_tag.text.replace(u'\xa0', u'').replace(u'\r', u'').replace(u'\n', u'')
      
#     question_code_flag = 0
#     if (
#         re.compile(r"\(\d{8}\w\)").search(text) != None
#     ):  # verify that the question title text has the document code, example (55036821C)
#         if (
#             question_code_flag == 2
#         ):  # condition to stop if two different question titles have the same document code
#             question_code_flag = 0
#             continue
#         else:
#             question_code = text.split()[-1]
#             question_code_flag = 1
#             # Sometimes the first question has FR and the second NL and vice versa, this is a check for it.

#             try:
#                 if h2_tag.span["lang"] == "FR":
#                     question_FR = text
#                     start_with = text.split("à")[0]
                   
#                     end_with = text.split("à")[1]
#                     politician_adressed = end_with.split("(")[0].strip()
#                     if "Question de" in start_with:
#                         politician_asking = start_with.split("de")[1].strip()
#                     elif  "-" in start_with:
#                         politician_asking = " ".join(start_with.split()[1:])    
#                 elif h2_tag.span["lang"] == "NL":
#                     question_NL = text
#                     start_with = text.split("aan")[0].strip()
#                     end_with = text.split("aan")[1].strip()
#                     politician_adressed = end_with.split("(")[0].strip()
#                     if "Vraag van" in start_with:
#                         politician_asking = start_with.split("Vraag van")[1].strip()
#                     elif  "-" in start_with:
#                         politician_asking = " ".join(start_with.split()[1:]).strip()     
    
#             except:
#                 print("problem with span lang attribute.")
#                 print(h2_tag.span)
            
#             question_text = ""
#             counter = 0
#             for p_tag in h2_tag.find_next_siblings("p"):
#                 p_text = p_tag.text.replace(u'\xa0', u'').replace(u'\r', u'').replace(u'\n', u'')
                
#                 if re.compile(r'\d\d.\d\d').search(p_text) and politician_asking in p_text:
#                     if counter == 1:
#                         counter = 0
#                         continue
#                     else:
#                         question_text += p_text
#                         text_start = p_text.split()[0]
#                         print(text_start)
#                         counter += 1
#                     for next_p_tag in p_tag.find_next_siblings("p"):
#                         next_p_text = next_p_tag.text.replace(u'\xa0', u'').replace(u'\r', u'').replace(u'\n', u'')
#                         if re.compile(r'\d\d.\d\d').search(next_p_text) and (next_p_text.split()[0] != text_start or politician_asking in next_p_text) :
#                             break
#                         else:
#                             question_text += next_p_text

            
            
                
                        
#             for next_h2_tag in h2_tag.find_next_siblings("h2"):
#                 next_text = next_h2_tag.text.strip()
#                 if question_code in next_text:
#                     question_code_flag = 2
#                     try:
#                         if next_h2_tag.span["lang"] == "FR":
#                             question_FR = next_text
#                         elif next_h2_tag.span["lang"] == "NL":
#                             question_NL = next_text
#                     except:
#                         print("problem with span lang attribute.")
#                         print(h2_tag.span)
#                     questions.append(
#                             {
#                                 "title": "",
#                                 "document_number": "",
#                                 "date": "",
#                                 "document_page_url": "main_url",
#                                 "main-title": "",
#                                 "link_to_document": "",
#                                 "keywords": "",
#                                 "source": "",
#                                 "commissionchambre": '',
#                                 "fr_text": question_FR,
#                                 "nl_text": question_NL,
#                                 "stakeholders": [
#                                     politician_asking,
#                                     politician_adressed,
#                                 ],
#                                 "question_text" : question_text,
#                                 "status": "",
#                                 "title_embedding": [],
#                                 "fr_text_embedding": [],
#                                 "nl_text_embedding": [],
#                                 "topic": "",
#                                 "policy level": "",
#                                 "type": "",
#                                 "issue": "",
#                                 "reference": "",
#                             }
#                         )
                    
#                     break    





# import string
# from typing import Text
# questions = []

# test_url = "https://www.lachambre.be/doc/CCRI/html/55/ic1162x.html"
# test_response = requests.get(test_url)
# test_soup = bs(test_response.content, "html.parser")
# for h2_tag in test_soup.find_all("h2"):
#     text = h2_tag.text.replace(u'\xa0', u'').replace(u'\r', u'').replace(u'\n', u'')
     
#     question_code_flag = 0
#     if (
#         re.compile(r"\(\d{8}\w\)").search(text) != None
#     ):  # verify that the question title text has the document code, example (55036821C)
#         if (
#             question_code_flag == 2
#         ):  # condition to stop if two different question titles have the same document code
#             question_code_flag = 0
#             continue
#         else:
#             counter = 0 
#             print("setting counter to 0 at start")
#             question_code = text.split()[-1]
#             print(question_code)
#             print("--------------")
#             question_code_flag = 1
#             # Sometimes the first question has FR and the second NL and vice versa, this is a check for it.
#             print("level 1 before first quesion language check")
#             print("----------------------------------")
#             try:
#                 if h2_tag.span["lang"] == "FR":
#                     question_FR = text
#                     start_with = text.split("à")[0]
                   
#                     end_with = text.split("à")[1]
#                     politician_adressed = end_with.split("(")[0].strip()
#                     if "Question de" in start_with:
#                         politician_asking = start_with.split("de")[1].strip()
#                     elif  "-" in start_with:
#                         politician_asking = " ".join(start_with.split()[1:])    
#                 elif h2_tag.span["lang"] == "NL":
#                     question_NL = text
#                     start_with = text.split("aan")[0].strip()
#                     end_with = text.split("aan")[1].strip()
#                     politician_adressed = end_with.split("(")[0].strip()
#                     if "Vraag van" in start_with:
#                         politician_asking = start_with.split("Vraag van")[1].strip()
#                     elif  "-" in start_with:
#                         politician_asking = " ".join(start_with.split()[1:]).strip()     
    
#             except:
#                 print("problem with span lang attribute.")
#                 print(h2_tag.span)
#             print("level 1 after first language check")
#             print("----------------------------------")
#             question_text = ""
#             if counter == 1:
#                 print("  counter just before check for 1 before p_tag loop")
#                 counter = 0
#                 print("  counter after check for 1 and reset before p_tag loop")
#                 continue
#             print("counter before first p_tag loop", counter)
#             print("-------------------")
#             text_start_list = []
#             counter_two = 0
#             for p_tag in h2_tag.find_next_siblings("p"):
#                 counter_two += 1
#                 print("counter_two is ")
#                 print(counter_two)
#                 print()
#                 print("level 2 first p_tag loop")
#                 print("---------------------------")
#                 p_text = p_tag.text.replace(u'\xa0', u'').replace(u'\r', u'').replace(u'\n', u'')
                
#                 if re.compile(r'\d\d.\d\d').search(p_text) and politician_asking in p_text:
#                     print("    counter after first p_tag loop ", counter)
#                     print("  p_text first 20.....")
#                     print(f'  {p_text[:20]}')
#                     print("  --------------")
#                     text_start = p_text[:5]
#                     if text_start in text_start_list:
#                         print("    text_start already used, continue to next")
#                         print("   setting counter to 1")
#                         print("   ------------------------")
#                         counter += 1
#                     else:
#                         text_start_list.append(text_start)
#                         print("appending start_text to list")       
#                         print("    getting text_start after check for code")
#                         print(text_start)
#                         print("---------------------------------")
#                         if counter == 1:
#                             print("  counter just before check for 1")
#                             counter = 0
#                             print("  counter after check for 1 and reset")
#                             print("  continue ...")
#                             continue
#                         else:
#                             print("    counter before gettng text_start")
#                             question_text += p_text
#                             print("    question_text after check for counter")
#                             print(len(question_text))
#                             print("    start of question_text")
#                             print(question_text[:40])
#                             print("    end of question_text")
#                             print(question_text[-40:])
#                             print("----------------------------")
                            
#                             counter += 1
#                             print("    counter after getting text_start ", counter)
#                             print("    ----------------------------")
#                             for next_p_tag in p_tag.find_next_siblings("p"):
#                                 next_p_text = next_p_tag.text.replace(u'\xa0', u'').replace(u'\r', u'').replace(u'\n', u'')
#                                 print("      next_p_text first 20 ......")
#                                 print(next_p_text[:20])
#                                 print("      --------------------")
#                                 if re.compile(r'^\d\d.\d\d').search(next_p_text) and text_start not in next_p_text[:5] :
#                                     print(f"      text_start just before break")
#                                     print(text_start)
#                                     print("      break here")
#                                     break
#                                 else:
#                                     question_text += next_p_text
#                                     print("      question_text")
#                                     print(len(question_text))
#                                     print("    start of question_text")
#                                     print(question_text[:40])
#                                     print("    end of question_text")
#                                     print(question_text[-40:])
#                                     print("      ------------------")

                         
                        
#             for next_h2_tag in h2_tag.find_next_siblings("h2"):
#                 next_text = next_h2_tag.text.strip()
#                 if question_code in next_text:
#                     question_code_flag = 2
#                     try:
#                         if next_h2_tag.span["lang"] == "FR":
#                             question_FR = next_text
#                         elif next_h2_tag.span["lang"] == "NL":
#                             question_NL = next_text
#                     except:
#                         print("problem with span lang attribute.")
#                         print(h2_tag.span)
#                     questions.append(
#                             {
#                                 "title": "",
#                                 "document_number": "",
#                                 "date": "",
#                                 "document_page_url": "main_url",
#                                 "main-title": "",
#                                 "link_to_document": "",
#                                 "keywords": "",
#                                 "source": "",
#                                 "commissionchambre": '',
#                                 "fr_text": question_FR,
#                                 "nl_text": question_NL,
#                                 "stakeholders": [
#                                     politician_asking,
#                                     politician_adressed,
#                                 ],
#                                 "question_text" : question_text,
#                                 "status": "",
#                                 "title_embedding": [],
#                                 "fr_text_embedding": [],
#                                 "nl_text_embedding": [],
#                                 "topic": "",
#                                 "policy level": "",
#                                 "type": "",
#                                 "issue": "",
#                                 "reference": "",
#                             }
#                         )
                    
#                     break    

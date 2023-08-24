import json
from sentence_transformers import SentenceTransformer
import re
import certifi
from bs4 import BeautifulSoup
import requests
import pandas as pd
import json
from functools import partial
import itertools
from concurrent.futures import ThreadPoolExecutor
from dateutil import parser
import os
import pymongo
from dotenv import load_dotenv
from datetime import date
load_dotenv()

def finding_true_link():
    today = date.today()

    week = today.isocalendar().week
    year =today.isocalendar().year
    
    for days in range(week, 1, -1):
        resp = requests.get(f"https://www.lachambre.be/emeeting/api/meetings/week/{year}/{days}/calendar.xml")
        soup = BeautifulSoup(resp.text, 'html.parser')
        if soup.meetings.meeting:
            xml_url = f"https://www.lachambre.be/emeeting/api/meetings/week/{year}/{days}/calendar.xml"
            break
    return xml_url

session = requests.Session()

def extract_main(xml_url):
    response = requests.get(xml_url)

    if response.status_code == 200:
        xml_content = response.content
    else:
        print("Failed to fetch XML content.")
        exit()

    soup = BeautifulSoup(xml_content, 'xml')

    language = 'nl' 
    meetings_data = [] # list of dictionaries

    meetings = soup.find_all('meeting')

    for meeting in meetings:
        title = meeting.find('label', {'lang': language}).text
        organ = meeting.find('organ').text
        date = meeting.find('date').text
        time = meeting.find('time').text
        status = meeting.find('status').text
        room = meeting.find('label', {'lang': language}).text
        meeting_number = meeting.find('meetingNumber').text

        meeting_info = {
            "title": title,
            "organ": organ,
            "date": date,
            "time": time,
            "status": status,
            "room": room,
            "meeting_number": meeting_number
        }

        meetings_data.append(meeting_info)


    links = []
    for meeting_info in meetings_data:
        link = f"https://www.lachambre.be/emeeting/api/meetings/{meeting_info['organ']}/{meeting_info['status']}/{meeting_info['date']}/{meeting_info['meeting_number']}/agenda.xml"
        links.append(link)
    return links

def flip_date(date :str)-> str :
    date_flip = date.split('-')
    return date_flip[2]+'/'+date_flip[1]+'/'+date_flip[0]

def extract_url(xml_page_url):
    xml_data=xml_page_url.split("/")
    date = xml_data[-3]
    organ = xml_data[-5]
    Number = xml_data[-2]
    status = xml_data[-4]
    return f'https://www.lachambre.be/emeeting/?organ={organ}&status={status}&date={date}&number={Number}'

def extract_data(xml_page_url, session):

    agenda_response = session.get(xml_page_url)

    if agenda_response.status_code == 200:
        agenda_xml_content = agenda_response.content
    else:
        print("Failed to fetch XML content.")
        exit()
    soup = BeautifulSoup(agenda_xml_content, 'xml')
    print(soup)

    page_date = flip_date(soup.date.text)
    page_url = extract_url(xml_page_url)

    items = soup.find_all('item')
    total_items = []

    for item in items:
        print("Item:")
        paras = item.find_all('para')
        for para in paras:
            nl_text = para.description('label')[0].text
            fr_text = para.description('label')[1].text
            data_items ={"nl_text":nl_text,"fr_text":fr_text}

            if para.annexes:
                link = para.link('label')[0].text
                data_items['link_to_document'] = link

            total_items.append(data_items)
    return total_items
    

    page_dict={
        "date":page_date,
        "document_page_url":page_url,
        "title_nl":soup.meeting('label', lang='nl')[0].text,
        "title_fr":soup.meeting('label', lang='fr')[0].text,
        "items": total_items
        }
    return page_dict

def extract_agenda(links,session):
    agenda=[]
    for link in links:
        agenda.append(extract_data(link, session))
    return agenda



def transform(agenda_data):
    
    final_data = process_and_save_embeddings(extract_stakeholders(agenda_data), model_name='sentence-transformers/LaBSE')
    return final_data
    
def extract_stakeholders(agenda_data):
    
    data_with_names = []
    
    pattern1 = r'Question de (.*?)\s+\('
    pattern2 = r'Proposition de loi \((.*?)\)'
    pattern3 = r'Interpellation de (.*?) [à \ a]' 
    pattern4 = r'Proposition de résolution \((.*?)\)'

    for item in agenda_data:
        if 'items' in item:
            for para_item in item['items']:
                fr_text = para_item['fr_text']

                match_name = re.search(pattern1, fr_text)
                if match_name:
                    name = match_name.group(1)
                    para_item['Stakeholders'] = name

                matches_other = re.findall(pattern2, fr_text)
                if matches_other:
                    if 'Stakeholders' in para_item:
                        para_item['Stakeholders'] += ', ' + ', '.join(matches_other)
                    else:
                        para_item['Stakeholders'] = ', '.join(matches_other)

                match_pattern3 = re.search(pattern3, fr_text)
                if match_pattern3:
                    name_pattern3 = match_pattern3.group(1)
                    if 'Stakeholders' in para_item:
                        para_item['Stakeholders'] += ', ' + name_pattern3
                    else:
                        para_item['Stakeholders'] = name_pattern3

                # Check for pattern4 (Proposition de résolution) and add it to 'Stakeholders' field
                match_pattern4 = re.search(pattern4, fr_text)
                if match_pattern4:
                    name_pattern4 = match_pattern4.group(1)
                    if 'Stakeholders' in para_item:
                        para_item['Stakeholders'] += ', ' + name_pattern4
                    else:
                        para_item['Stakeholders'] = name_pattern4

                data_with_names.append(para_item)

    return agenda_data


def process_and_save_embeddings(agenda_data, model_name='sentence-transformers/LaBSE'):
     
    model = SentenceTransformer(model_name)

    
    for item in agenda_data:
        if 'items' in item:
            for para_item in item['items']:
                nl_text = para_item['nl_text'] 
                nl_text_embedding = model.encode(nl_text)
                para_item['nl_text_embedding'] = nl_text_embedding.tolist()
                fr_text = para_item['fr_text']
                fr_text_embedding = model.encode(fr_text)
                para_item['fr_text_embedding'] = fr_text_embedding.tolist()
    
    return agenda_data

xml_url = finding_true_link()
links = extract_main(xml_url)
agenda_data = extract_agenda(links,session)
final_data=transform(agenda_data)

mongodb_url = os.getenv("MONGODB_URI")
database_name = "akkanto_db"
collection_name = "agenda"
client = pymongo.MongoClient(mongodb_url)
database = client[database_name]
collection = database[collection_name]

for agenda in final_data:
        agenda_url = agenda["document_page_url"]
        existing_article = collection.find_one({"document_page_url": agenda_url})
        if not existing_article:
            collection.insert_one(agenda)

client.close()

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

def extract_url(soup):
    date = soup.date.text
    organ = soup.organ.text
    Number = soup.meetingNumber.text
    status = soup.status.text
    return f'https://www.lachambre.be/emeeting/?organ={organ}&status={status}&date={date}&number={Number}'

def extract_data(xml_page_url, session):

    agenda_response = session.get(xml_page_url)

    if agenda_response.status_code == 200:
        agenda_xml_content = agenda_response.content
    else:
        print("Failed to fetch XML content.")
        exit()
    soup = BeautifulSoup(agenda_xml_content, 'xml')
    
    page_date = flip_date(soup.date.text)
    page_url = extract_url(soup)

    all_items = soup.find_all('item')
    
    total_items = []

    for data in all_items:
        nl_text = data.description('label')[0].text
        fr_text = data.description('label')[1].text
        data_items ={"nl_text":nl_text,"fr_text":fr_text}

        if data.annexes:
            link = data.link('label')[0].text
            data_items['link_to_document'] = link
            
        total_items.append(data_items)
    

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

agenda_data_all = []

xml_url = finding_true_link()
links = extract_main(xml_url)
agenda_data = extract_agenda(links,session)


json_filename = "agenda_corrected.json"
with open(json_filename, mode='w', encoding='utf-8') as json_file:
    json.dump(agenda_data, json_file, indent=4, ensure_ascii=False)
        
print(f"Extracted data saved to '{json_filename}'")
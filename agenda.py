import requests
import xml.etree.ElementTree as ET
import csv

def extract_agenda_data(link):
    response = requests.get(link)
    if response.status_code == 200:
        xml_string = response.text
        root = ET.fromstring(xml_string)
        
        agenda_data = []
        
        para_elements = root.findall(".//para")
        
        for para in para_elements:
            description_element = para.find(f".//description/label[@lang='{language}']")
            description = description_element.text.strip() if description_element is not None else None
            
            annex_element = para.find("annexes/annex")
            annex_label_element = annex_link_element = None
            
            if annex_element is not None:
                annex_label_element = annex_element.find(f".//description/label[@lang='{language}']")
                annex_label = annex_label_element.text.strip() if annex_label_element is not None else None
                
                annex_link_element = annex_element.find(f".//link/label[@lang='{language}']")
                annex_link = annex_link_element.text.strip() if annex_link_element is not None else None
            else:
                annex_label = None
                annex_link = None
            
            agenda_item = {
                "description": description,
                "annex_label": annex_label,
                "annex_link": annex_link
            }
            
            agenda_data.append(agenda_item)
        
        return agenda_data
    else:
        print(f"Failed to fetch agenda XML from link: {link}")
        return []

xml_url = "https://www.lachambre.be/emeeting/api/meetings/week/2023/29/calendar.xml"
response = requests.get(xml_url)

if response.status_code == 200:
    xml_content = response.content
else:
    print("Failed to fetch XML content.")
    exit()

# Parse the XML using xml.etree.ElementTree
root = ET.fromstring(xml_content)

language = 'nl'  # Change this to 'fr' if you want the French data
meetings_data = []

meetings = root.findall(".//meeting")

for meeting in meetings:
    title_element = meeting.find(f"title/label[@lang='{language}']")
    if title_element is not None:
        title = title_element.text
    else:
        title = None
    
    organ_element = meeting.find('organ')
    organ = organ_element.text if organ_element is not None else None
    
    date_element = meeting.find('date')
    date = date_element.text if date_element is not None else None
    
    time_element = meeting.find('time')
    time = time_element.text if time_element is not None else None
    
    status_element = meeting.find('status')
    status = status_element.text if status_element is not None else None
    
    room_element = meeting.find('room/label')
    room = room_element.text if room_element is not None else None
    
    meeting_number_element = meeting.find('meetingNumber')
    meeting_number = meeting_number_element.text if meeting_number_element is not None else None
    
    agenda_link = f"https://www.lachambre.be/emeeting/api/meetings/{organ}/{status}/{date}/{meeting_number}/agenda.xml"
    agenda_data = extract_agenda_data(agenda_link)
    
    meeting_info = {
        "title": title,
        "organ": organ,
        "date": date,
        "time": time,
        "status": status,
        "room": room,
        "meeting_number": meeting_number,
        "agenda_data": agenda_data
    }
    
    meetings_data.append(meeting_info)


# Save the combined data as a CSV file
csv_filename = "agenda_data.csv"
with open(csv_filename, mode='w', newline='', encoding='utf-8') as csv_file:
    fieldnames = ["title", "date", "time",  "room", "description", "annex_label", "annex_link"]
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
    writer.writeheader()
    
    for meeting_info in meetings_data:
        for agenda_item in meeting_info["agenda_data"]:
            writer.writerow({
                "title": meeting_info["title"],
                
                "date": meeting_info["date"],
                "time": meeting_info["time"],
                
                "room": meeting_info["room"],
                
                "description": agenda_item["description"],
                "annex_label": agenda_item["annex_label"],
                "annex_link": agenda_item["annex_link"]
            })

print(f"Data saved to {csv_filename}")



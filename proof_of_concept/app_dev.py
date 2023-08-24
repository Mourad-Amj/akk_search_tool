# Streamlit proof of concept
# Run this with 
# python -m streamlit run proof_of_concept/app.py
#mongodb+srv://maximberge:aAIbS7zRpsbsy6Gb@cluster0.p97p1.mongodb.net/?retryWrites=true&w=majority

# imports
import streamlit as st
import pandas as pd
import io
import xlsxwriter
import pymongo
#msg pack
from bson import json_util
import json
import os
from sentence_transformers import SentenceTransformer, util
import datetime
st.set_page_config(page_title = "Search engine")


#connection
connection = 'mongodb+srv://maximberge:aAIbS7zRpsbsy6Gb@cluster0.p97p1.mongodb.net/?retryWrites=true&w=majority'

@st.cache_resource
def init_connection():
    return pymongo.MongoClient(connection)

client = init_connection()

#Used to save db into file
def save_db_json(db_to_save):
    # with open(db_to_save, "rb") as data_file:
    #          agenda_db_file = json.load(data_file)

    #     agenda_db = agenda_db_file
    return None

def load_db_json():
    cached_agenda_db_file_path = "agenda_db.json"
    cached_doc_db_file_path = "doc_db.json"
    
    cached_pleniere_db_file_path = "pleneiere_db.json"
    cached_commission_db_file_path = "commission_db.json"
    
    with open(cached_agenda_db_file_path, "rb") as data_file:
             agenda_db_file = json.load(data_file)

    agenda_db = agenda_db_file
    
    with open(cached_doc_db_file_path, "rb") as data_file:
            doc_db_file = json.load(data_file)

    doc_db = doc_db_file
    
    #updated
    with open(cached_pleniere_db_file_path, "rb") as data_file:
            pleniere_db_file = json.load(data_file)

    pleniere_db = pleniere_db_file
    
    with open(cached_commission_db_file_path, "rb") as data_file:
            commission_db_file = json.load(data_file)

    commissions_db = commission_db_file
    
    return 


#Added Plenieres and commissions
#adding cache data reduces considerably the loading time.
@st.cache_data
def get_data():
    
    #---------------------------------------------------------------------LOADING FROM FILE
    cached_agenda_db_file_path = "agenda_db.json"
    cached_doc_db_file_path = "doc_db.json"
    
    cached_pleniere_db_file_path = "pleneiere_db.json"
    cached_commission_db_file_path = "commission_db.json"
    
    
    
    
    if os.path.isfile(cached_agenda_db_file_path) and os.path.isfile(cached_doc_db_file_path) and os.path.isfile(cached_pleniere_db_file_path) and os.path.isfile(cached_commission_db_file_path) :
        
        with open(cached_agenda_db_file_path, "rb") as data_file:
             agenda_db_file = json.load(data_file)

        agenda_db = agenda_db_file
        
        with open(cached_doc_db_file_path, "rb") as data_file:
             doc_db_file = json.load(data_file)

        doc_db = doc_db_file
        
        #updated
        with open(cached_pleniere_db_file_path, "rb") as data_file:
             pleniere_db_file = json.load(data_file)

        pleniere_db = pleniere_db_file
        
        with open(cached_commission_db_file_path, "rb") as data_file:
             commission_db_file = json.load(data_file)

        commissions_db = commission_db_file
        agenda_db, doc_db, pleniere_db, commissions_db = load_db_json()
        
    else: #No file then create
        db = client.akkanto_db
        
        #To optimize later on
        agenda_db_cursor= db.agenda_test.find()
        doc_db_cursor = db.doc_test.find()
        pleniere_db_cursor = db.seances_plenieres_compte_rendu_integral.find()
        commissions_db_cursor = db.commissions_compte_rendu_integral.find()
        
        doc_db = list(doc_db_cursor)
        agenda_db = list(agenda_db_cursor)
        pleniere_db = list(pleniere_db_cursor)
        commissions_db = list(commissions_db_cursor)
        
        serialized_agenda = [json.dumps(result, default=json_util.default, separators=(',', ':')) for result in agenda_db]
        serialized_doc = [json.dumps(result, default=json_util.default, separators=(',', ':')) for result in doc_db]
        serialized_pleniere = [json.dumps(result, default=json_util.default, separators=(',', ':')) for result in pleniere_db]
        serialized_commissions = [json.dumps(result, default=json_util.default, separators=(',', ':')) for result in commissions_db]
        
        
        with io.open('agenda_db.json', 'w', encoding='utf8') as outfile:
            data_agenda = json.dumps(serialized_agenda,indent=4)
            outfile.write(data_agenda)
            
        
        with io.open('docs_db.json', 'w', encoding='utf8') as outfile:
            data_docs = json.dumps(serialized_doc,indent=4)
            outfile.write(data_docs)
            
        with io.open('plenieres.json', 'w', encoding='utf8') as outfile:
            data_pleniere = json.dumps(serialized_pleniere,indent=4)
            outfile.write(data_pleniere)
        
        with io.open('commissions_db.json', 'w', encoding='utf8') as outfile:
            data_commissions = json.dumps(serialized_commissions,indent=4)
            outfile.write(data_commissions)
            
            #--------------------------HAD TO COMMENT BC OF EMBED
        # embedder = SentenceTransformer('LaBSE')
        # for item1 in agenda_db:
        #     item1["embedding"] = embedder.encode(item1["issue"], convert_to_tensor=False)
        # for item2 in doc_db:
        #     #using text not title
        #     item2["embedding"] = embedder.encode(item2["text"], convert_to_tensor=False)    
        
     
    return agenda_db, doc_db, pleniere_db, commissions_db
#---------------------------------------------------------------------------------------------

#database is documents
agenda, database, pleniere, commission = get_data()

# Print results.---------------------------------------TEST OF CONNECTION-------------------
# for item in agenda:
#     st.write(item['issue'])

# for element in agenda:
#     print(element)


# -----------------------------------END OF CONNECTION----------------------------


# initialization
st.title("PoC: lachambre.be custom search engine")

#moved search bar from 235
search = st.text_input('Type your search')






def apply_topic_filter(database, score_threshold):
    search_result = []
    for item in database: 
        
        #--------------------HAD TO COMMENT BC OF EMBED
        
        # cos_score = util.cos_sim(item["embedding"], query_embedding)[0]
        # condition = cos_score.abs()
        # if condition > score_threshold :
            search_result.append(item)
    return search_result

#@st.cache_data
def apply_date_filter(database, start_date, end_date):
    search_result = []
    for item in database: 
        item_date = datetime.datetime.strptime(item['date'], '%d/%m/%Y').date()
        if item_date < start_date or item_date > end_date:
            continue
        else:
            search_result.append(item)
    return search_result
    
# ----------------------------------------------------------------------
# Load environment
# ----------------------------------------------------------------------

# agenda = load_agenda()
# database = load_data()


# ----------------------------------------------------------------------
# Parameters
# ----------------------------------------------------------------------

language = st.radio(
    "Output language: ",
    ('fr', 'nl'))

# ----------------------------------------------------------------------
### Filters sub-section
# ----------------------------------------------------------------------

st.subheader("Filters")
col1, col2= st.columns(2)

# ---
# Search filter
# ---

# Text field + processing query

with col2:
    # Slider to tune the threshold on cos similarity
    score_threshold = st.slider('Filtering threshold: ', 0.0, 0.5, 0.35)
    st.write("Cosine similarity set at", score_threshold)
    st.info('Filter by relevance', icon="ℹ️")
    
# Date filter 
with col1:
# Date filter 
    #st.date_input("test date",format="DD/MM/YYYY")

    # Initializing default dates settings. Runs once.
    if 'start_date' not in st.session_state:
        st.session_state['start_date'] = datetime.date.today() - datetime.timedelta(days=730)
    if 'end_date' not in st.session_state:
        st.session_state['end_date'] = datetime.date.today()
    # Creating the widgets.    
    start_date = st.date_input('Start date', st.session_state['start_date'], format="DD/MM/YYYY")
    end_date = st.date_input('End date', st.session_state['end_date'], format="DD/MM/YYYY")
    if start_date < end_date:
        st.success('Start date (default: 2 weeks ago): `%s`\n\nEnd date (default: today):`%s`' % (start_date, end_date))
    else:
        st.error('Error: End date must fall after start date.')

    # Update session state when dates are changed
    if start_date != st.session_state['start_date']:
        st.session_state['start_date'] = start_date
    if end_date != st.session_state['end_date']:
        st.session_state['end_date'] = end_date

 
# Applying the filters

embedder = SentenceTransformer('all-MiniLM-L6-v2')
#search = st.text_input('Type your search')
query_embedding = embedder.encode(search, convert_to_tensor=False)


agenda_search = apply_topic_filter(apply_date_filter(agenda, start_date, end_date), score_threshold)
doc_search = apply_topic_filter(apply_date_filter(database, start_date, end_date), score_threshold)

try:
    agenda_temp = pd.DataFrame(agenda_search)
    agenda_out = agenda_temp#[['r', 'level', 'type', 'issue', 'date', 'authors', 'url', 'status']]
except Exception as e :
    st.write(e)
    st.write("367")
    agenda_out = pd.DataFrame(agenda_search)

try:
    df_temp = pd.DataFrame(doc_search)
    df_out = df_temp[['id', 'title', 'author', 'date', 'source', 'text']]
except Exception as e:
    st.write(e)
    df_out = pd.DataFrame(doc_search)

st.write("Agenda: ")
agenda_out = st.data_editor(agenda_out, hide_index=True, num_rows = "dynamic", use_container_width= True)
st.write("Looking back: ")
try:
    
    df_out = st.data_editor(df_out, hide_index=True, num_rows = "dynamic", use_container_width= True)
except:
    pass
if "agenda_df" not in st.session_state:
    st.session_state['agenda_df'] = pd.DataFrame(columns=['r', 'level', 'type', 'issue', 'date', 'authors', 'url', 'status'])

if "output_df" not in st.session_state:
    st.session_state['output_df'] = pd.DataFrame(columns=['id', 'title', 'author', 'date', 'source', 'text'])


if st.button("Append search result"):
    # update dataframe state
    st.session_state.agenda_df = pd.concat([st.session_state.agenda_df, agenda_out], axis=0, ignore_index=True).drop_duplicates(subset='issue', keep="last")
    st.session_state.output_df = pd.concat([st.session_state.output_df, df_out], axis=0, ignore_index=True).drop_duplicates(subset='id', keep="last")

    
    st.text("Updated dataframe")




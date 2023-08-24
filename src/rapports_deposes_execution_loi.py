"""
Scrape the data from the 'Rapports déposés en exécution d'une loi' page of the lachambre.be site.
"""
import json
import time
import pandas as pd
import pymongo
import certifi
import os
import ssl
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
ssl._create_default_https_context = ssl._create_unverified_context
start_time = time.perf_counter()

url = "https://www.lachambre.be/kvvcr/showpage.cfm?section=none&language=fr&cfm=/site/wwwcfm/rajv/rajvlist.cfm"

load_dotenv()
connection = os.getenv("MONGODB_URI")
client = pymongo.MongoClient(connection, tlsCAFile=certifi.where())
db = client["akkanto_db"]
col = db["rapports_deposes_final"]

# Get the two tables (with the column names and the content) from the url
dfs = pd.read_html(url)
df_titles = dfs[0].dropna(how="all", axis=1)
df_content = dfs[1].dropna(how="all").dropna(how="all", axis=1)

# Combine the two last columns
df_content[5] = df_content[5].astype(str) + "-" + df_content[6]
df_content = df_content.drop(df_content.columns[[4]], axis=1)

# Add column names to the content table
df_content.columns = df_titles.iloc[0].tolist()

model = SentenceTransformer("sentence-transformers/LaBSE")
# embedder function
def embedder(doc):
    
    embedding = model.encode(doc, convert_to_tensor=False)
    return embedding


# adding new columns to the df
df_content["fr_source"] = ["Contrôle Rapports déposés en exécution d'une loi"] * len(
    df_content.index
)
df_content["document_page_url"] = [
    "https://www.lachambre.be/kvvcr/showpage.cfm?section=none&language=fr&cfm=/site/wwwcfm/rajv/rajvlist.cfm"
] * len(df_content.index)
df_content["type"] = ["Report"] * len(df_content.index)
df_content["stakeholders"] = ["Not applicable"] * len(df_content.index)

# format changes to make to the df before saving
df_content.rename(columns={"Annonce": "date"}, inplace=True)
df_content.rename(columns={"Rapport": "fr_text"}, inplace=True)
df_content.rename(columns={"Loi & Article": "fr_title"}, inplace=True)
df_content.rename(columns={"Periodicité": "frequency"}, inplace=True)
df_content["issue"] = df_content["fr_text"] + " " + df_content["fr_title"]



# Export to json file
# df_content.to_json(
#     "data/rapports_deposes_execution_loi.json", orient="records", force_ascii=False
# )
rapports_list = df_content.to_dict(orient="records")

for rapport in rapports_list:

    if col.find_one({"fr_text": rapport["fr_text"]}):
        print("Document with the same doc_number already exists.")
        
    else:
        rapport["fr_title_embedding"] = embedder(rapport["fr_title"]).tolist()
        rapport["fr_text_embedding"] = embedder(rapport["fr_text"]).tolist()
        print("Adding new document ...")
        col.insert_one(rapport)  

end_time = time.perf_counter()
print(round(end_time - start_time, 2), "seconds")
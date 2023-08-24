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


# dutch page scraping
url_fr = "https://www.lachambre.be/kvvcr/showpage.cfm?section=none&language=fr&cfm=/site/wwwcfm/rajv/rajvlist.cfm"

load_dotenv()
connection = os.getenv("MONGODB_URI")
client = pymongo.MongoClient(connection, tlsCAFile=certifi.where())
db = client["akkanto_db"]
col = db["rapports_deposes_final"]

# Get the two tables (with the column names and the content) from the url
dfs_fr = pd.read_html(url_fr)
df_titles_fr = dfs_fr[0].dropna(how="all", axis=1)
df_content_fr = dfs_fr[1].dropna(how="all").dropna(how="all", axis=1)

# Combine the two last columns
df_content_fr[5] = df_content_fr[5].astype(str) + "-" + df_content_fr[6]
df_content_fr = df_content_fr.drop(df_content_fr.columns[[4]], axis=1)

# Add column names to the content table
df_content_fr.columns = df_titles_fr.iloc[0].tolist()


url_fr = "https://www.lachambre.be/kvvcr/showpage.cfm?section=none&language=fr&cfm=/site/wwwcfm/rajv/rajvlist.cfm"
url_nl = "https://www.lachambre.be/kvvcr/showpage.cfm?section=none&language=nl&cfm=/site/wwwcfm/rajv/rajvlist.cfm"

# Get the two tables (with the column names and the content) from the url
dfs_fr = pd.read_html(url_fr)
df_titles_fr = dfs_fr[0].dropna(how="all", axis=1)
df_content_fr = dfs_fr[1].dropna(how="all").dropna(how="all", axis=1)


dfs_nl = pd.read_html(url_nl)
df_titles_nl = dfs_nl[0].dropna(how="all", axis=1)
df_content_nl = dfs_nl[1].dropna(how="all").dropna(how="all", axis=1)

# Combine the two last columns
df_content_fr[5] = df_content_fr[5].astype(str) + "-" + df_content_fr[6]
df_content_fr = df_content_fr.drop(df_content_fr.columns[[4]], axis=1)

df_content_nl[5] = df_content_nl[5].astype(str) + "-" + df_content_nl[6]
df_content_nl = df_content_nl.drop(df_content_nl.columns[[4]], axis=1)

# Add column names to the content table
df_content_fr.columns = df_titles_fr.iloc[0].tolist()
df_content_nl.columns = df_titles_nl.iloc[0].tolist()


# Incorporating french scraping to dutch scraping
df_content_nl_copy = df_content_nl[["Verslag", "Wet & Artikel"]].copy()

df_content_fr["nl_text"] = df_content_nl_copy["Verslag"]
df_content_fr["nl_title"] = df_content_nl_copy["Wet & Artikel"]


df_content = df_content_fr

model = SentenceTransformer("sentence-transformers/LaBSE")


# embedder function
def embedder(doc):
    embedding = model.encode(doc, convert_to_tensor=False)
    return embedding


# adding new columns to the df
df_content["fr_source"] = ["Contrôle Rapports déposés en exécution d'une loi"] * len(
    df_content.index
)
df_content["nl_source"] = [
    "Controle Verslagen ingediend ter uitvoering van een wet"
] * len(df_content.index)
df_content["document_page_url"] = [
    "https://www.lachambre.be/kvvcr/showpage.cfm?section=none&language=fr&cfm=/site/wwwcfm/rajv/rajvlist.cfm"
] * len(df_content.index)
df_content["type"] = ["Report"] * len(df_content.index)
df_content["fr_stakeholders"] = ["Not applicable"] * len(df_content.index)
df_content["nl_stakeholders"] = ["Not applicable"] * len(df_content.index)
df_content["fr_keywords"] = ["Not applicable"] * len(df_content.index)
df_content["nl_keywords"] = ["Not applicable"] * len(df_content.index)
df_content["commissionchambre"] = ["Not applicable"] * len(df_content.index)
df_content["policy_level"] = ["Federal Parliament"] * len(df_content.index)

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
    if col.find_one({"fr_text": {"$eq": rapport["fr_text"]}}):
        print("Document with the same doc_number already exists.")

    else:
        rapport["fr_title_embedding"] = embedder(rapport["fr_title"]).tolist()
        rapport["fr_text_embedding"] = embedder(rapport["fr_text"]).tolist()
        rapport["nl_title_embedding"] = embedder(rapport["nl_title"]).tolist()
        rapport["nl_text_embedding"] = embedder(rapport["nl_text"]).tolist()
        print("Adding new document ...")
        col.insert_one(rapport)

end_time = time.perf_counter()
print(round(end_time - start_time, 2), "seconds")

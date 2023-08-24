"""
Scrape the data from the 'Rapports déposés en exécution d'une loi' page of the lachambre.be site.
"""
import json
import pandas as pd
from sentence_transformers import SentenceTransformer

url = "https://www.lachambre.be/kvvcr/showpage.cfm?section=none&language=fr&cfm=/site/wwwcfm/rajv/rajvlist.cfm"

# Get the two tables (with the column names and the content) from the url
dfs = pd.read_html(url)
df_titles = dfs[0].dropna(how="all", axis=1)
df_content = dfs[1].dropna(how="all").dropna(how="all", axis=1)

# Combine the two last columns
df_content[5] = df_content[5].astype(str) + "-" + df_content[6]
df_content = df_content.drop(df_content.columns[[4]], axis=1)

# Add column names to the content table
df_content.columns = df_titles.iloc[0].tolist()


# embedder function
def embedder(doc):
    model = SentenceTransformer("sentence-transformers/LaBSE")
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

# embedding + new columns for embedding
df_content["fr_title_embedding"] = embedder(df_content["fr_title"]).tolist()
df_content["fr_text_embedding"] = embedder(df_content["fr_text"]).tolist()

# Export to json file
df_content.to_json(
    "data/rapports_deposes_execution_loi.json", orient="records", force_ascii=False
)

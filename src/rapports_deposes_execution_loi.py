"""
Scrape the data from the 'Rapports déposés en exécution d'une loi' page of the lachambre.be site.
"""
import pandas as pd

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

# Export to json file
df_content.to_json(
    "data/rapports_deposes_execution_loi.json", orient="records", force_ascii=False
)

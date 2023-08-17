# Streamlit proof of concept
# Run this with 
# streamlit run proof_of_concept/main.py

# imports
import streamlit as st
import pandas as pd
import io
import xlsxwriter
# Write files to in-memory strings using BytesIO
# See: https://xlsxwriter.readthedocs.io/workbook.html?highlight=BytesIO#constructor

# initialization
st.title("PoC: lachambre.be custom search engine")

# load dataframe


# create text field
# output: search string
search = st.text_input('Type your search')
# apply search in dataframe
# input: search string, output: new dataframe
# df_out = semantic_search(df, search)
df_out = pd.DataFrame({'Data': [11, 12, 13, 14]})

# write excel
# input: dataframe, output: excel file (as a variable)
buffer = io.BytesIO()

with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
    df_out.to_excel(writer, sheet_name='Sheet1')
    writer.close()
# create download button
# output: download excel
    st.download_button(
        label="Download Excel worksheets",
        data=buffer,
        file_name="pandas_multiple.xlsx",
        mime="application/vnd.ms-excel"
    )





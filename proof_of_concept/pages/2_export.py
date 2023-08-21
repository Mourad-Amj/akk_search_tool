import streamlit as st
import pandas as pd
import io
import xlsxwriter

from sentence_transformers import SentenceTransformer, util
import datetime



try:
    
    #Export
    #st.info('Export the Saved Result', icon="ℹ️")
    with pd.ExcelWriter(st.session_state['buffer'], engine='xlsxwriter') as writer:
            st.session_state['saved_df'].to_excel(writer, sheet_name='Sheet1')
            st.download_button(
                label="Download Excel worksheets",
                data=st.session_state['buffer'],
                file_name="pandas_multiple.xlsx",
                mime="application/vnd.ms-excel"
            )
    
    #Print saved data
    st.write(st.session_state['saved_df'])
    

    #Export
    #st.info('Export the Saved Result', icon="ℹ️")
    with pd.ExcelWriter(st.session_state['buffer'], engine='xlsxwriter') as writer:
            st.session_state['saved_df'].to_excel(writer, sheet_name='Sheet1')
            st.download_button(
                label="Download Excel worksheets",
                data=st.session_state['buffer'],
                file_name="pandas_multiple.xlsx",
                mime="application/vnd.ms-excel"
            )
except:
    st.subheader("No data to export")
    st.text("Data will appear once a search has been processed")
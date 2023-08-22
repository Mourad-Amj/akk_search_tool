import streamlit as st
import pandas as pd
import io




try:
    try:
        st.write("Agenda: ")
        st.session_state.agenda_df=st.session_state.agenda_df[['r', 'level', 'type', 'issue', 'date', 'authors', 'url', 'status']]
        st.dataframe(st.session_state.agenda_df, use_container_width=True)
    except:
        st.subheader("No Agenda to export")
        st.text("Agenda will appear once a search result is appended")
    try:
        st.write("Looking back: ")    
        st.session_state.output_df=st.session_state.output_df[['id', 'title', 'author', 'date', 'source', 'text']]
        st.dataframe(st.session_state.output_df, use_container_width=True)
    except:
        st.subheader("No data to export")
        st.text("Data will appear once a search result is appended")
    
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        agenda = pd.DataFrame(st.session_state.agenda_df)
        agenda.to_excel(writer, sheet_name='Sheet1')        
        output = pd.DataFrame(st.session_state.output_df)
        output.to_excel(writer, sheet_name='Sheet1')
        writer.close()

            st.download_button(
                label="Download Excel worksheets",
                data=buffer,
                file_name="output_df.xlsx",
                mime="application/vnd.ms-excel"
            )

except:
    st.subheader("No data to export")
    st.text("Data will appear once a search has been processed")
  
  

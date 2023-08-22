import streamlit as st
import pandas as pd
import io


try:
    if st.session_state['edited_df'].empty:
        st.subheader("No data to export")
        st.text("Data will appear once a search has been processed")
    else:
        st.data_editor(st.session_state['edited_df'], num_rows="dynamic")
        #st.dataframe(st.session_state['edited_df'], use_container_width=True)
        buffer = io.BytesIO()

        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            output = pd.DataFrame(st.session_state.edited_df)
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
  
  

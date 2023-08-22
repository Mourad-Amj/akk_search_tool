import streamlit as st
import pandas as pd
import io


try:
    st.dataframe(st.session_state.output_df, use_container_width=True)
    buffer = io.BytesIO()

    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
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
  
  
#Notes : it displays 2 df, one with delete checkmark, the other without, checkmark does
#nothing for the moment
  
def callback():
    edited_rows = st.session_state["data_editor"]["edited_rows"]
    rows_to_delete = []

    for idx, value in edited_rows.items():
        if value["x"] is True:
            rows_to_delete.append(idx)

    st.session_state["saved_df"] = (
        st.session_state["saved_df"].drop(rows_to_delete, axis=0).reset_index(drop=True)
    )
    df_temp = pd.DataFrame(search_result)
    df_out = df_temp[['id', 'title', 'author', 'date', 'source', 'text']]
    st.session_state['saved_df'] = df_out
    #delete rows func
    columns = st.session_state["saved_df"].columns
    column_config = {column: st.column_config.Column(disabled=True) for column in columns}

    modified_df = st.session_state["saved_df"].copy()
    modified_df["x"] = False
    # Make Delete be the first column
    modified_df = modified_df[["x"] + modified_df.columns[:-1].tolist()]

    st.data_editor(
    modified_df,
    key="data_editor",
    on_change=callback,
    hide_index=True,
    column_config=column_config,
    )
    st.dataframe(st.session_state['saved_df'], hide_index=True, use_container_width= True)
    
import streamlit as st
import pandas as pd
import io
import pandas as pd
import xlsxwriter


class Printer():
    def __init__(self, writer, offset = 1) -> None:
        self.index = offset
        self.sheet_name = "Output"
        self.buffer = buffer
        self.writer = writer
        self.workbook  = self.writer.book
        self.worksheet = self.workbook.add_worksheet(self.sheet_name)
        # Creating a color palette
        self.colors = {
            'blue': '427A82',
            'green': 'D4B36A',
            'yellow': 'D4726A',
            'orange': 'D49D6A',
            'gray': '797D7D'
        }
        # Defining a few formats
        self.bold = self.workbook.add_format({"bold": True})
        self.header_format = self.workbook.add_format(
            {
                "bold": True,
                "text_wrap": True,
                "valign": "top",
                "bg_color": self.colors['gray'],
                "border": 1,
            }
        )
        self.title_format = self.workbook.add_format(
            {
                "bold": True,
                "text_wrap": True,
                "valign": "top",
                "bg_color": self.colors['orange'],
                "font_color": "FFFFFF"
            }
        )
        self.sheet_name = 'Output'

    def append_df(self, df) -> None:
        for col_num, value in enumerate(df.columns.values):
            self.worksheet.write(self.index, col_num, value, self.header_format)
        df.to_excel(self.writer, sheet_name=self.sheet_name, startrow = self.index + 1, index = False, header = False)
        
        self.index = self.index + df.shape[0] + 1

    def type_text(self, text, column = 0, format = {'bold' : False, 'size': 14}) -> None:
        self.worksheet.write(self.index, column, text)
        self.index = self.index + 1

    def insert_title(self, text):

        self.worksheet.set_row(self.index, cell_format=self.title_format)
        self.type_text(text, column = 1)
        self.index = self.index + 1

    def convert_col(self, col):
        return f'{chr(64+col)}'

    def format_source(self, column, text_match, format):
        self.worksheet.conditional_format(f'{self.convert_col(column)}1:{self.convert_col(column)}{self.index + 5}', {'type':     'text',
                                       'criteria': 'containing',
                                       'value':    text_match,
                                       'format':   format})

    def autofit(self):
        self.worksheet.autofit()

    def test_create_excel(self):
        df_dict_1 = {
        'onderwerp': ['School', 'Kwaliteit'],
        'Bron' : ['Vlaams', 'Vlaams'],
        'Brontype': ['Plenaire', 'Plenaire'],
        'Kwestie': ['De sterke toename van ', 'Bespreking van het ontwerp van decreet over leersteun'],
        'Opmerkingen' : ['link1', 'link2']
        }
        df_dict_2 = {
        'onderwerp': ['Kwaliteit', 'Kwaliteit'],
        'Bron' : ['Vlaams', 'Vlaams'],
        'Brontype': ['Plenaire', 'Website'],
        'Kwestie': ['De plenaire vergadering bespreekt het ontwerp.', 'De plenaire vergadering bespreekt het ontwerp.'],
        'Opmerkingen' : ['link3', 'link4']
        }
        self.test_df1 = pd.DataFrame(df_dict_1)
        self.test_df2 = pd.DataFrame(df_dict_2)
        self.type_text('Wekelijkse politieke monitoring', format = self.bold)
        self.append_df(self.test_df1, self.header_format)    
        self.append_df(self.test_df2, self.header_format)

# Piece of code to convert urls to hyperlinks
"""
df["url"] = df["url"].apply(lambda url : '=HYPERLINK("{}", "{}")'.format("url", "LINK") )
"""

try:
    try:
        st.write("Agenda: ")
        st.session_state.agenda_df=st.session_state.agenda_df[['r', 'level', 'type', 'issue', 'date', 'authors', 'url', 'status']]
        st.session_state.agenda_df = st.data_editor(st.session_state.agenda_df, num_rows = "dynamic", use_container_width=True, hide_index = True)
    except:
        st.subheader("No Agenda to export")
        st.text("Agenda will appear once a search result is appended")
    try:
        st.write("Looking back: ")    
        st.session_state.output_df=st.session_state.output_df[['id', 'title', 'author', 'date', 'source', 'text']]
        st.session_state.output_df=st.data_editor(st.session_state.output_df, num_rows = "dynamic", use_container_width=True, hide_index = True)
    except:
        st.subheader("No data to export")
        st.text("Data will appear once a search result is appended")
    

    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        printer = Printer(writer)
        printer.type_text('Weekly summary: ')
        printer.insert_title('1.  Agenda')
        printer.append_df(st.session_state.agenda_df)
        printer.insert_title('2.  Looking back')
        printer.append_df(st.session_state.output_df)
        printer.autofit()
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
  


import pandas as pd
import openpyxl
import xlsxwriter
from openpyxl.styles import PatternFill

class Printer():

    def __init__(self, test = False, file_name = 'output.xlsx', offset = 0) -> None:
        self.index = offset
        self.sheet_name = "Output"
        self.writer = pd.ExcelWriter(file_name, engine = "xlsxwriter")
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
                "fg_color": self.colors['gray'],
                "border": 1,
            }
        )
        self.title_format = self.workbook.add_format(
            {
                "bold": True,
                "text_wrap": True,
                "valign": "top",
                "fg_color": self.colors['orange'],
                "font_color": "FFFFFF"
            }
        )
        self.sheet_name = 'Output'
        if test:
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
            self.width = self.test_df1.shape[1]

    def append_df(self, df, header_format) -> None:
        for col_num, value in enumerate(df.columns.values):
            self.worksheet.write(0, self.index+ col_num + 1, value, header_format)
        df.to_excel(self.writer, sheet_name=self.sheet_name, startrow = self.index + 1, index = False, header = False)
        
        self.index = self.index + df.shape[0] + 1

    def type_text(self, text, column = 0, format = {'bold' : False, 'size': 14}) -> None:
        self.worksheet.write(self.index, column, text)
        self.index = self.index + 1

    def insert_title(self, text, color = 'orange'):
        self.color_current_row(color = color)
        self.type_text(text, column = 1)
        self.index = self.index + 1


    def convert_col(self, col):
        return f'{chr(64+col)}'

    def format_source(self, column, text_match, format):
        self.worksheet.conditional_format(f'{self.convert_col(column)}1:{self.convert_col(column)}{self.index + 5}', {'type':     'text',
                                       'criteria': 'containing',
                                       'value':    text_match,
                                       'format':   format})

    def test_create_excel(self):
        self.type_text('Wekelijkse politieke monitoring', format = self.bold)
        self.append_df(self.test_df1, self.header_format)    
        self.append_df(self.test_df2, self.header_format)

printer = Printer(test = True)
printer.test_create_excel()

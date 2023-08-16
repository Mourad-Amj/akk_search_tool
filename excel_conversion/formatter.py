import pandas as pd
import openpyxl
import xlsxwriter
from openpyxl.styles import PatternFill

class Printer():

    def __init__(self, test = False, file_name = 'output.xlsx', offset = 0) -> None:
        self.index = offset

        self.writer = pd.ExcelWriter(file_name, engine = "xlsxwriter")
        self.workbook  = self.writer.book
        self.worksheet = self.workbook.add_worksheet('Output')

        self.colors = {
            'blue': PatternFill(patternType='solid',fgColor='427A82'),
            'green': PatternFill(patternType='solid',fgColor='D4B36A'),
            'yellow': PatternFill(patternType='solid',fgColor='D4726A'),
            'orange': PatternFill(patternType='solid',fgColor='D49D6A'),
            'gray': PatternFill(patternType='solid',fgColor='797D7D')
        }
        self.bold = self.workbook.add_format({"bold": True})
 
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

    def append_df(self, df) -> None:
        df.to_excel(self.workbook, sheet_name=self.sheet_name, startrow = self.index, index = False)
        self.index = self.index + df.shape[0] + 1

    def type_text(self, text, column = 0, format = {'bold' : False, 'size': 14}) -> None:
        self.worksheet.write(self.index, column, text)
        self.index = self.index + 1

    def insert_title(self, text, color = 'orange'):
        self.color_current_row(color = color)
        self.type_text(text, column = 1)
        self.index = self.index + 1

    def color_current_row(self, color = 'blue'):
        for column in range(self.width):
            self.color_cell(self.index, column, color)

    def color_cell(self, row, col, color = 'blue'):
        self.worksheet.cell(row = row, column = col).fill = self.colors[color]


    def test_create_excel(self):
        self.type_text('Wekelijkse politieke monitoring', format = self.bold)
        self.insert_title('1.  Op de agenda')
        self.color_current_row(self.colors['gray'])
        self.append_df(self.test_df1)
        self.insert_title('2.  Looking back')
        self.append_df(self.test_df2)

printer = Printer(test = True)
printer.test_create_excel()

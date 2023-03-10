from datetime import date

import openpyxl
import db

workbook = openpyxl.load_workbook(r'\\172.16.245.8\QlikView\XLS\Reliability\Отчет%20по%20компаниям_2403_07-03-2023.xlsx')
try:
    sheet = workbook['Worksheet']
except KeyError:
    sheet = workbook['Sheet1']
today = date.today()

insert_data = []
for row in sheet.iter_rows(min_row=5, values_only=True):
    row_data = ()
    for value in row:
        if value is not None:
            row_data += (str(value),)
    row_data += (today.strftime("%Y-%m-%d"),)
    insert_data.append(row_data)

# print(len(insert_data))
# print(insert_data[0])
# print(insert_data[-1])
# print(len(insert_data[0]))
db.insert_data_adata(insert_data)

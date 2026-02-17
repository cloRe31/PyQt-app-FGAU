from openpyxl import Workbook, load_workbook

wb = load_workbook(filename = 'Cartriges.xlsx')
sheet_ranges = wb['']
print(sheet_ranges['D18'].value)
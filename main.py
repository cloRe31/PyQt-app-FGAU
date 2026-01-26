from PyQt6.QtWidgets import QApplication, QWidget, QMainWindow, QPushButton, QComboBox, QLabel, QLayout
from PyQt6.QtCore import QSize, Qt
from openpyxl import Workbook

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        opertation_combobox = QComboBox()
        opertation_combobox.addItems(["Поставка", "Расход"])
        














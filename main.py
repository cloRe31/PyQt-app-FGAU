from PyQt6.QtWidgets import (QApplication, QWidget, QLabel, QComboBox, QVBoxLayout, QHBoxLayout, QStackedWidget, QLineEdit, QPushButton, QSizePolicy)
from PyQt6.QtCore import Qt
import sys
from openpyxl import Workbook

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.resize(1000, 600)
        self.setMinimumSize(600, 400)

        HLayout = QHBoxLayout(self)
        LVLayout = QVBoxLayout()
        RVLayout = QVBoxLayout()
        

        operation_combobox = QComboBox()
        operation_combobox.addItems(["Расход", "Поставка"])
        operation_combobox.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Fixed
        )
        operation_combobox.setMinimumWidth(200)
        operation_combobox.setMaximumWidth(400)

        container_combobox = QHBoxLayout()
        container_combobox.addStretch()
        container_combobox.addWidget(operation_combobox)
        container_combobox.addStretch()
        container_combobox.setStretch(0, 1)
        container_combobox.setStretch(1, 6)
        container_combobox.setStretch(2, 1)
        LVLayout.addLayout(container_combobox)

        self.pages = Pages()
        RVLayout.addWidget(self.pages)

        operation_combobox.currentTextChanged.connect(self.pages.setPage)
        

        HLayout.addLayout(LVLayout)
        HLayout.addLayout(RVLayout)
        HLayout.setStretch(0, 1)
        HLayout.setStretch(1, 1)


class Pages(QWidget):
    def __init__(self):
        super().__init__()

        self.stack = QStackedWidget()
        PageLayout = QVBoxLayout(self)
        PageLayout.addWidget(self.stack)

        self.pagesDict = {
            "Расход": ExpensesPage(),
            "Поставка": SupplyPage()
        }

        for page in self.pagesDict.values():
            self.stack.addWidget(page)
        
    def setPage(self, name):
        self.stack.setCurrentWidget(self.pagesDict[name])

class ExpensesPage(QWidget):
    def __init__(self):
        super().__init__()

        VLayout = QVBoxLayout(self)
        HLayout = QHBoxLayout()

        HLayout.addStretch()
        HLayout.addWidget(QLabel("Расходы"))
        HLayout.addStretch()

        HLayout.setStretch(0, 2)
        HLayout.setStretch(1, 7)
        HLayout.setStretch(2, 1)
        VLayout.addLayout(HLayout)

class SupplyPage(QWidget):
    def __init__(self):
        super().__init__()

        VLayout = QVBoxLayout(self)
        VLayout.addWidget(QLabel("Поставка"))
        


app = QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec()

        









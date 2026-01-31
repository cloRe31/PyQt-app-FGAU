from PyQt6.QtWidgets import (QApplication, QWidget, QLabel, QComboBox, QVBoxLayout, QHBoxLayout, QGroupBox, QStackedWidget, QLineEdit, QPushButton, QSizePolicy)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QIntValidator
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

        container_combobox = QHBoxLayout()

        operation_combobox = QComboBox()
        operation_combobox.addItems(["Расход", "Поставка"])
        operation_combobox.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Fixed
        )
        operation_combobox.setMinimumWidth(200)
        operation_combobox.setMaximumWidth(400)

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

        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(15)
        main_layout.addStretch()

        # ===== Блок: Название картриджа =====
        name_group = QGroupBox("Название картриджа")
        name_layout = QVBoxLayout(name_group)

        name_layout.addWidget(QLabel("Введите название картриджа:"))
        self.NameLine = QLineEdit()
        name_layout.addWidget(self.NameLine)

        main_layout.addWidget(name_group)

        # ===== Блок: Количество =====
        quantity_group = QGroupBox("Количество")
        quantity_layout = QVBoxLayout(quantity_group)

        quantity_layout.addWidget(QLabel("Введите количество:"))
        self.QuantityLine = QLineEdit()
        self.QuantityLine.setValidator(QIntValidator(0, 1_000_000))
        quantity_layout.addWidget(self.QuantityLine)

        main_layout.addWidget(quantity_group)

        # ===== Блок: Действие =====
        action_group = QGroupBox("Действие")
        action_layout = QVBoxLayout(action_group)

        write_btn = QPushButton("Записать")
        action_layout.addWidget(write_btn)

        self.ApproveText = QLabel("Расход записан")
        self.ApproveText.setStyleSheet("color: green; font-weight: bold;")
        self.ApproveText.hide()
        action_layout.addWidget(self.ApproveText)

        write_btn.clicked.connect(self.btnClicked)

        main_layout.addWidget(action_group)
        main_layout.addStretch()

    def btnClicked(self):
        name = self.NameLine.text().strip()
        quantity = self.QuantityLine.text()

        if not name and not quantity:
            self.showMessage("Введите данные", "red")
            return

        if not name:
            self.showMessage("Введите название картриджа", "red")
            return

        if not quantity:
            self.showMessage("Введите количество", "red")
            return


        quantity = int(quantity) if quantity else 0

        #далее логика с Excel

        self.showMessage("Расход записан", "green")

        self.NameLine.clear()
        self.QuantityLine.clear()

    def showMessage(self, text, color):
        self.ApproveText.hide()
        self.ApproveText.setText(text)
        self.ApproveText.setStyleSheet(f"color: {color}; font-weight: bold;")
        self.ApproveText.show()

        QTimer.singleShot(2_000, self.ApproveText.hide)




class SupplyPage(QWidget):
    def __init__(self):
        super().__init__()

        VLayout = QVBoxLayout(self)

        


app = QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec()

        









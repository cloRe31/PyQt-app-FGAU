from PyQt6.QtWidgets import (QApplication, QWidget, QLabel, QComboBox, QVBoxLayout, QHBoxLayout, 
                             QGroupBox, QDateEdit, QStackedWidget, QLineEdit, QPushButton, QSizePolicy)
from PyQt6.QtCore import Qt, QTimer, QDate
from PyQt6.QtGui import QIntValidator
import sys
import sqlite3

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

        self.db = DatabaseManager()
        self.pages = Pages(self.db)
        RVLayout.addWidget(self.pages)

        operation_combobox.currentTextChanged.connect(self.pages.setPage)
        
        HLayout.addLayout(LVLayout)
        HLayout.addLayout(RVLayout)
        HLayout.setStretch(0, 1)
        HLayout.setStretch(1, 1)


class Pages(QWidget):
    def __init__(self, db):
        super().__init__()
        self.db = db

        self.stack = QStackedWidget()
        PageLayout = QVBoxLayout(self)
        PageLayout.addWidget(self.stack)

        self.pagesDict = {
            "Расход": ExpensesPage(self.db),
            "Поставка": SupplyPage(self.db)
        }

        for page in self.pagesDict.values():
            self.stack.addWidget(page)
        
    def setPage(self, name):
        self.stack.setCurrentWidget(self.pagesDict[name])

class OperationPage(QWidget):
    def __init__(self, db):
        super().__init__()
        self.db = db

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setSpacing(15)
        self.main_layout.addStretch()

        # ===== Блок: Название картриджа =====
        name_group = QGroupBox()
        name_layout = QVBoxLayout(name_group)

        name_layout.addWidget(QLabel("Выберите картридж"))
        self.CartridgeName = QComboBox()
        name_layout.addWidget(self.CartridgeName)
        self.load_cartriges()

        self.main_layout.addWidget(name_group)

        # ===== Блок: Количество =====
        quantity_group = QGroupBox()
        quantity_layout = QVBoxLayout(quantity_group)

        quantity_layout.addWidget(QLabel("Введите количество:"))
        self.QuantityLine = QLineEdit()
        self.QuantityLine.setValidator(QIntValidator(0, 1_000_000))
        quantity_layout.addWidget(self.QuantityLine)

        self.main_layout.addWidget(quantity_group)

        # ===== Блок: Доп поля =====
        self.extra_fields_layout = QVBoxLayout()
        self.extra_fields_layout.setSpacing(15)

        self.main_layout.addLayout(self.extra_fields_layout)
        self.setup_extra_fields()

        # ===== Блок: Дата =====
        date_group = QGroupBox()
        date_layout = QVBoxLayout(date_group)

        date_layout.addWidget(QLabel("Выберите дату"))
        self.DateLine = QDateEdit()
        self.DateLine.setCalendarPopup(True)
        self.DateLine.setDate(QDate.currentDate())
        date_layout.addWidget(self.DateLine)

        self.main_layout.addWidget(date_group)

        # ===== Блок: Кнопка =====
        action_group = QGroupBox()
        action_layout = QVBoxLayout(action_group)

        write_btn = QPushButton("Записать")
        action_layout.addWidget(write_btn)

        self.ApproveText = QLabel()
        self.ApproveText.hide()
        action_layout.addWidget(self.ApproveText)

        write_btn.clicked.connect(self.btnClicked)

        self.main_layout.addWidget(action_group)
        self.main_layout.addStretch()
        
        for group in (name_group, quantity_group, date_group, action_group):
            group.setStyleSheet("""
                QGroupBox {
                    border: none;
                }
            """)
        
    def load_cartriges(self):
        data = self.db.GetCartridges()
        for name, id in data:
            self.CartridgeName.addItem(name, id)

    def get_common_data(self):
        quantity = int(self.QuantityLine.text())
        cartridge_id = self.CartridgeName.currentData()
        date = self.DateLine.date().toString("yyyy-MM-dd")
        return quantity, cartridge_id, date

    def btnClicked(self):
        data = self.get_common_data()
        self.process_operation(self, data)
        #тут какая-то загвоздка
        #ТАКЖЕ ДОПИСАТЬ ЛОГИКУ В SUPPLYPAGE ТАКУЮ ЖЕ КАК И EXPENSESPAGE
        self.QuantityLine.clear()
    
    def process_operation(self):
        raise NotImplementedError

    def showMessage(self, text, color):
        self.ApproveText.hide()
        self.ApproveText.setText(text)
        self.ApproveText.setStyleSheet(f"color: {color}; font-weight: bold;")
        self.ApproveText.show()

        QTimer.singleShot(2_000, self.ApproveText.hide)
        
    def addSupply(self):
        cartridge_id = self.CartridgeName.currentData()
        quantity = int(self.QuantityLine.text())
        date = self.DateLine.date().toString("dd-MM-yyyy")
        self.db.addSupply(quantity, cartridge_id, date)
    
    def setup_extra_fields(self):
        pass

class ExpensesPage(OperationPage):
    def __init__(self, db):
        super().__init__(db)

    def process_operation(self, data):
        quantity, cartridge_id, date = data
        self.db.addExpense(quantity, cartridge_id, date)

    def setup_extra_fields(self):
        pass


class SupplyPage(OperationPage):
    def __init__(self, db):
        super().__init__(db)

    def setup_extra_fields(self):
        pass


class DatabaseManager():
    def __init__(self):
        self.conn = sqlite3.connect("Data/database.db")
        self.cursor = self.conn.cursor()

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS Cartridges (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE
                        )
        """)
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS Expenses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        quantity INTEGER,
        cartridge_id INTEGER,
        date DATE,
        FOREIGN KEY (cartridge_id) REFERENCES Cartridges(id)
                        )
        """)
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS Supplies (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        quantity INTEGER,
        cartridge_id INTEGER,
        date DATE,
        FOREIGN KEY (cartridge_id) REFERENCES Cartridges(id)
                        )
        """)
        self.conn.commit()
    
        self.cursor.execute("SELECT COUNT(*) FROM Cartridges")
        if self.cursor.fetchone()[0] == 0:
            self.load_from_excel()

    def load_from_excel(self):
        from openpyxl import load_workbook

        wb = load_workbook("Data/Cartridges.xlsx")
        ws = wb.active

        for name in ws.iter_rows(min_row=6, max_col=1, values_only=True):
            if name[0]:
                self.cursor.execute(
                    "INSERT INTO Cartridges (name) VALUES (?)",
                    (name[0],)
                )
            else: 
                break
        self.conn.commit()
    
    def GetCartridges(self):
        self.cursor.execute("SELECT id, name FROM Cartridges")
        return [(name, id) for id, name in self.cursor.fetchall()]
    
    def addExpense(self, quantity, cartridge_id, date):
        self.cursor.execute(
            "INSERT INTO Expenses (quantity, cartridge_id, date) VALUES (?,?,?)",
            (quantity, cartridge_id, date)
        )
        self.conn.commit()
    
    def addSupply(self, quantity, cartridge_id, date):
        self.cursor.execute(
            "INSERT INTO Supplies (quantity, cartridge_id, date) VALUES (?,?,?)",
            (quantity, cartridge_id, date)
        )
        self.conn.commit()

        

app = QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec()

        









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

        main_layout = QHBoxLayout(self)
        left_layout = QVBoxLayout()
        right_layout = QVBoxLayout()

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
        left_layout.addLayout(container_combobox)

        self.db = DatabaseManager()
        self.pages = Pages(self.db)
        right_layout.addWidget(self.pages)

        operation_combobox.currentTextChanged.connect(self.pages.set_page)
        
        main_layout.addLayout(left_layout)
        main_layout.addLayout(right_layout)
        main_layout.setStretch(0, 1)
        main_layout.setStretch(1, 1)


class Pages(QWidget):
    def __init__(self, db):
        super().__init__()
        self.db = db

        self.stack = QStackedWidget()
        page_layout = QVBoxLayout(self)
        page_layout.addWidget(self.stack)

        self.pages_dict = {
            "Расход": ExpensesPage(self.db),
            "Поставка": SupplyPage(self.db)
        }

        for page in self.pages_dict.values():
            self.stack.addWidget(page)
        
    def set_page(self, name):
        self.stack.setCurrentWidget(self.pages_dict[name])

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
        self.cartridge_name = QComboBox()
        name_layout.addWidget(self.cartridge_name)
        self.load_cartridges()

        self.main_layout.addWidget(name_group)

        # ===== Блок: Количество =====
        quantity_group = QGroupBox()
        quantity_layout = QVBoxLayout(quantity_group)

        quantity_layout.addWidget(QLabel("Введите количество:"))
        self.quantity_input = QLineEdit()
        self.quantity_input.setValidator(QIntValidator(1, 1_000_000))
        quantity_layout.addWidget(self.quantity_input)

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
        self.date_input = QDateEdit()
        self.date_input.setCalendarPopup(True)
        self.date_input.setDate(QDate.currentDate())
        date_layout.addWidget(self.date_input)

        self.main_layout.addWidget(date_group)

        # ===== Блок: Кнопка =====
        action_group = QGroupBox()
        action_layout = QVBoxLayout(action_group)

        write_btn = QPushButton("Записать")
        action_layout.addWidget(write_btn)

        self.approve_text = QLabel()
        self.approve_text.hide()
        action_layout.addWidget(self.approve_text)

        write_btn.clicked.connect(self.btn_clicked)

        self.main_layout.addWidget(action_group)
        self.main_layout.addStretch()
        
        for group in (name_group, quantity_group, date_group, action_group):
            group.setStyleSheet("""
                QGroupBox {
                    border: none;
                }
            """)
        
    def load_cartridges(self):
        data = self.db.get_cartridges()
        for name, cartridge_id in data:
            self.cartridge_name.addItem(name, cartridge_id)

    def get_raw_data(self):
        return {
            "quantity": self.quantity_input.text().strip(),
            "cartridge_id": self.cartridge_name.currentData(),
            "date": self.date_input.date().toString("yyyy-MM-dd")
        }
    
    def validate_form(self, data):
        if not data["quantity"]:
            return "Введите количество"
        
    def normalize_data(self, data):
        data["quantity"] = int(data["quantity"])

        return data
        
    def btn_clicked(self):
        data = self.get_raw_data()
        error = self.validate_form(data)

        if error:
            self.show_message(error, "red")
            return
        
        self.normalize_data(data)
        self.process_operation(data)

        self.show_message("Успешно записано", "green")
        self.quantity_input.clear()
    
    def process_operation(self):
        raise NotImplementedError

    def show_message(self, text, color):
        self.approve_text.hide()
        self.approve_text.setText(text)
        self.approve_text.setStyleSheet(f"color: {color}; font-weight: bold;")
        self.approve_text.show()

        QTimer.singleShot(2_000, self.approve_text.hide)
    
    def setup_extra_fields(self):
        pass

class ExpensesPage(OperationPage):
    def __init__(self, db):
        super().__init__(db)

    def process_operation(self, data):
        self.db.add_expense(data["quantity"], data["cartridge_id"], data["date"])

    def setup_extra_fields(self):
        pass


class SupplyPage(OperationPage):
    def __init__(self, db):
        super().__init__(db)

    def process_operation(self, data):
        self.db.add_supply(data["quantity"], data["cartridge_id"], data["date"])

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
    
    def get_cartridges(self):
        self.cursor.execute("SELECT id, name FROM Cartridges")
        return [(name, cartridge_id) for cartridge_id, name in self.cursor.fetchall()]
    
    def add_expense(self, quantity, cartridge_id, date):
        self.cursor.execute(
            "INSERT INTO Expenses (quantity, cartridge_id, date) VALUES (?,?,?)",
            (quantity, cartridge_id, date)
        )
        self.conn.commit()
    
    def add_supply(self, quantity, cartridge_id, date):
        self.cursor.execute(
            "INSERT INTO Supplies (quantity, cartridge_id, date) VALUES (?,?,?)",
            (quantity, cartridge_id, date)
        )
        self.conn.commit()

        

app = QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec()

        









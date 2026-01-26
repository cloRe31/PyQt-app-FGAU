from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QComboBox, QVBoxLayout, QHBoxLayout, QStackedWidget
import sys
from openpyxl import Workbook

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.resize(900, 600)
        self.setMinimumSize(600, 400)

        HLayout = QHBoxLayout(self)
        LVLayout = QVBoxLayout(self)
        RVLayout = QVBoxLayout(self)

        HLayout.setStretch(0,1)
        HLayout.setStretch(1,2)

        operation_combobox = QComboBox()
        operation_combobox.addItems(["Расход", "Поставка"])
        LVLayout.addWidget(operation_combobox)
        

        Label = QLabel("авироивырп")
        RVLayout.addWidget(Label)


        HLayout.addLayout(LVLayout)
        HLayout.addLayout(RVLayout)


app = QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec()

        









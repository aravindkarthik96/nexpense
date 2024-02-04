from PyQt6.QtWidgets import QDialog, QTableWidget, QTableWidgetItem, QVBoxLayout, QPushButton, QLineEdit
from PyQt6.QtCore import Qt
from numpy import empty
from constants import SHEET_ID

from main.google_apis.sheets_apis import get_sheets_serivce, upload_new_tag

class TagsDialog(QDialog):
    def __init__(self, creds, tags, parent=None):
        super().__init__(parent)
        self.creds = creds
        self.setWindowTitle("Available Tags")
        self.setGeometry(100, 100, 300, 200)  # Adjust size as needed

        self.layout = QVBoxLayout(self)
        self.table = QTableWidget(self)
        self.table.setColumnCount(1)  # Assuming each tag is just a string
        self.table.setHorizontalHeaderLabels(["Tags"])
        self.populate_table(tags)
        self.layout.addWidget(self.table)

        self.add_tag_button = QPushButton("Add Tag", self)
        self.add_tag_button.clicked.connect(self.add_new_tag_row)
        self.layout.addWidget(self.add_tag_button)
        self.table.itemChanged.connect(self.on_item_changed)

    def populate_table(self, tags):
        self.table.setRowCount(len(tags))
        for row, tag in enumerate(tags):
            self.table.setItem(row, 0, QTableWidgetItem(tag))

    def add_new_tag_row(self):
        row_position = self.table.rowCount()
        self.table.insertRow(row_position)
        new_item = QTableWidgetItem("")
        new_item.setFlags(new_item.flags() | Qt.ItemFlag.ItemIsEditable)
        self.table.setItem(row_position, 0, new_item)
        self.table.editItem(new_item)

    def on_item_changed(self, item):
        if(item.text() != "") :
            row = item.row()
            column = item.column()
            upload_new_tag(get_sheets_serivce(self.creds), SHEET_ID, item.text())
            print(f"Changed item at row {row}, column {column}")
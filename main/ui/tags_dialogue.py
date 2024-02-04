from PyQt6.QtWidgets import QDialog, QTableWidget, QTableWidgetItem, QVBoxLayout, QPushButton, QLineEdit
from PyQt6.QtCore import Qt

class TagsDialog(QDialog):
    def __init__(self, tags, parent=None):
        super().__init__(parent)
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

        # Option 1: Use QTableWidgetItem and set it to be editable
        new_item = QTableWidgetItem("")
        new_item.setFlags(new_item.flags() | Qt.ItemFlag.ItemIsEditable)
        self.table.setItem(row_position, 0, new_item)

        # Option 2: Use QLineEdit as an editor (comment out if using option 1)
        # line_edit = QLineEdit(self.table)
        # self.table.setCellWidget(row_position, 0, line_edit)

        self.table.editItem(new_item)  # Automatically start editing the new item
        # For QLineEdit, you might want to set the focus explicitly
        # line_edit.setFocus()

    def on_item_changed(self, item):
        print(f"New tag entered: {item.text()}")
        row = item.row()
        column = item.column()
        print(f"Changed item at row {row}, column {column}")

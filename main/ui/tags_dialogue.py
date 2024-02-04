from PyQt6.QtWidgets import QDialog, QTableWidget, QTableWidgetItem, QVBoxLayout

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

    def populate_table(self, tags):
        self.table.setRowCount(len(tags))
        for row, tag in enumerate(tags):
            self.table.setItem(row, 0, QTableWidgetItem(tag))
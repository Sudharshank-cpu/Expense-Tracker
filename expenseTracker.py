# Importing Modules
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QLineEdit, QComboBox, QDateEdit, QTableWidget, QVBoxLayout, QHBoxLayout, QMessageBox, QTableWidgetItem, QHeaderView
from PyQt5.QtSql import QSqlDatabase, QSqlQuery
from PyQt5.QtCore import QDate, Qt
import sys

# Creating Main Window Class
class ExpensesApp(QWidget):
    def __init__(self):
        super().__init__()

        # Main Window Created
        self.resize(550,500)
        self.setWindowTitle("Expense Tracker")

        # Creating Widgets
        self.dateBox = QDateEdit()
        self.dateBox.setDate(QDate.currentDate())
        self.dropDown = QComboBox()
        self.amount = QLineEdit()
        self.description = QLineEdit()

        self.addButton = QPushButton("Add Expense")
        self.deleteButton = QPushButton("Delete Expense")
        self.changeData = QPushButton("Edit Data")
        self.addButton.clicked.connect(self.addExpense)

        # Events Trigger
        self.deleteButton.clicked.connect(self.deleteExpense)
        self.changeData.clicked.connect(self.changeExpense)

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["ID", "Date", "Category", "Amount", "Description"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.sortByColumn(1, Qt.DescendingOrder)

        self.dropDown.addItems(["", "Food", "Transportation", "Rent", "Shopping", "Entertainment", "Bills", "Other"])

        # CSS Styles
        self.setStyleSheet('''
                           QWidget{
                           background-color: #b8c9e1;
                           }
                           QLabel{
                           color: #333;
                           font-size: 14px;
                           }
                           QLineEdit, QComboBox, QDateEdit{
                           background-color: #b8c9e1;
                           color: #333;
                           border: 1px solid #4f4;
                           padding: 5px;
                           }
                           QTableWidget{
                           background-color: #b8c9e1;
                           color: #333;
                           border: 1px solid #4f4;
                           }
                           QPushButton{
                           background-color: #4caf50;
                           color: #9ff;
                           border: None;
                           padding: 8px 16px;
                           font-size: 14px;
                           }
                           QPushButton:hover{
                           background-color: #45a049;
                           }
                           ''')

        # Designing Layouts
        self.masterLayout = QVBoxLayout()
        self.row = QHBoxLayout()
        self.row1 = QHBoxLayout()
        self.row2 = QHBoxLayout()

        self.row.addWidget(QLabel("Date:"))
        self.row.addWidget(self.dateBox)
        self.row.addWidget(QLabel("Category:"))
        self.row.addWidget(self.dropDown)

        self.row1.addWidget(QLabel("Amount:"))
        self.row1.addWidget(self.amount)
        self.row1.addWidget(QLabel("Description:"))
        self.row1.addWidget(self.description)

        self.row2.addWidget(self.addButton)
        self.row2.addWidget(self.deleteButton)
        self.row2.addWidget(self.changeData)

        self.masterLayout.addLayout(self.row)
        self.masterLayout.addLayout(self.row1)
        self.masterLayout.addLayout(self.row2)

        self.masterLayout.addWidget(self.table)

        self.setLayout(self.masterLayout)

    # Load Table from "expenses.sqlite" Data
    def loadTable(self):
        self.table.setRowCount(0)

        query = QSqlQuery("SELECT * FROM expenses")
        row = 0
        while query.next():
            expenseId = query.value(0)
            date = query.value(1)
            category = query.value(2)
            amount = query.value(3)
            description = query.value(4)

            self.table.insertRow(row)

            self.table.setItem(row, 0, QTableWidgetItem(str(expenseId)))    #Row, Column,data
            self.table.setItem(row, 1, QTableWidgetItem(date))
            self.table.setItem(row, 2, QTableWidgetItem(category))
            self.table.setItem(row, 3, QTableWidgetItem(str(amount)))
            self.table.setItem(row, 4, QTableWidgetItem(description))

            row += 1

    # Add Expenses from provided Data
    def addExpense(self):
        date = self.dateBox.date().toString("dd-MM-yyyy")
        category = self.dropDown.currentText()
        amount = self.amount.text()
        description = self.description.text()

        query = QSqlQuery()
        query.prepare('''
                      INSERT INTO expenses(date, category, amount, description)
                      VALUES(?, ?, ?, ?)
                      ''')
        query.addBindValue(date)
        if category=="":
            QMessageBox.warning(self, "Data Error", "Category was Empty. Add Data")
            return
        query.addBindValue(category)
        query.addBindValue(amount)
        query.addBindValue(description)
        query.exec_()

        self.dateBox.setDate(QDate.currentDate())
        self.dropDown.setCurrentIndex(0)
        self.amount.clear()
        self.description.clear()

        self.loadTable()

    # Delete Expenses from Database file
    def deleteExpense(self):
        selectedRow = self.table.currentRow()
        if selectedRow == -1:
            QMessageBox.warning(self, "No Expenses Chosen", "Please Choose an Expense to Delete!")
            return
        expenseId = int(self.table.item(selectedRow,0).text())

        confirm = QMessageBox.question(self, "Confirmation", "Are you sure to Delete Expenses?", QMessageBox.Yes | QMessageBox.No)
        if confirm == QMessageBox.No:
            return

        query = QSqlQuery()
        query.prepare("DELETE FROM expenses WHERE id = ?")
        query.addBindValue(expenseId)
        query.exec_()

        self.loadTable()

    # Change Expenses
    def changeExpense(self):
        selectedRow = self.table.currentRow()
        selectedCol = self.table.currentColumn()
        if selectedRow == -1:
            QMessageBox.warning(self, "No Expenses Chosen", "Please Choose an Expense to Edit!")
            return
        selectedData = self.table.item(selectedRow, selectedCol).text()
        QMessageBox.warning(self, "Confirmation", "Selected Data was {}".format(selectedData))

# Create and Connect Database
database = QSqlDatabase.addDatabase("QSQLITE")
database.setDatabaseName("expense.db")
if not database.open():
    QMessageBox.critical(None, "Error", "Could not Open \"expense.db\" Database\nMaybe, Database module wasnot able to Open")
    sys.exit(1)

# Executing "expenses.sqlite" Query File
query = QSqlQuery()
query.exec_("""
            CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            category TEXT,
            amount REAL,
            description TEXT
            )
            """)

# Execution
if __name__=="__main__":
    app = QApplication([])
    main = ExpensesApp()
    main.loadTable()
    main.show()
    app.exec_()

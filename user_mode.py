import os
import sqlite3

from PyQt6.QtCore import QSize, pyqtSignal, Qt
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QMainWindow, QTableWidgetItem, QMessageBox, QLabel
from ui_files.ui_user import Ui_MainWindow


class MainWindow(QMainWindow):
    closed = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.load_cars()
        self.ui.rent_button.clicked.connect(self.rent_car)

    def closeEvent(self, a0):
        self.closed.emit()
        a0.accept()

    def keyPressEvent(self, a0):
        if a0.key() == Qt.Key.Key_Escape:
            self.close()

    def rent_car(self):
        selected_row = self.ui.table.currentRow()
        car_id = selected_row + 1
        rented = int(self.ui.table.item(selected_row, 0).text())
        print(rented)
        conn = sqlite3.connect('cars.sqlite')
        cursor = conn.cursor()
        if rented == 0:
            cursor.execute(f'UPDATE cars SET is_rented = 1 WHERE id = {car_id}')
            reply = QMessageBox.question(self, 'Confirm', 'Save changes?',
                                         QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                         QMessageBox.StandardButton.No)

            if reply == QMessageBox.StandardButton.Yes:
                conn.commit()
                QMessageBox.information(self, 'Success', 'Changes saved')

            else:
                QMessageBox.information(self, 'Exit', 'Changes weren\'t saved')

        else:
            QMessageBox.information(self, 'Warning', 'Car is rented already')

        conn.close()
        self.load_cars()

    def load_cars(self):
        conn = sqlite3.connect('cars.sqlite')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM cars')
        cars = cursor.fetchall()
        self.ui.table.setRowCount(len(cars))
        self.ui.table.setColumnWidth(0, 50)
        for row_index, row_data in enumerate(cars):
            self.ui.table.setRowHeight(row_index, 200)
            for column_index, value in enumerate(row_data):
                if column_index != 0:
                    if column_index == 7:
                        self.ui.table.setItem(row_index, 0, QTableWidgetItem(str(value)))
                    if column_index == 6:
                        if os.path.isfile(value):
                            image = value
                        else:
                            image = 'resources/stock.jpg'
                        label = QLabel()
                        pixmap = QPixmap(image)
                        label.setPixmap(pixmap.scaled(QSize(300, 200)))
                        self.ui.table.setCellWidget(row_index, column_index, label)
                    else:
                        self.ui.table.setItem(row_index, column_index, QTableWidgetItem(str(value)))

        conn.close()

import os
import sqlite3

from PyQt6.QtCore import QSize, pyqtSignal, Qt
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QMainWindow, QWidget, QFileDialog, QMessageBox, QLabel, QTableWidgetItem

from ui_files.ui_admin import Ui_MainWindow
import ui_files.ui_edit_users
from admin import admin_windows


class MainWindow(QMainWindow):
    closed = pyqtSignal()
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.edit_users_button.clicked.connect(self.edit_users)
        self.ui.add_button.clicked.connect(self.add_car)
        self.ui.edit_button.clicked.connect(self.edit_selected_car)
        self.ui.delete_button.clicked.connect(self.delete_selected_car)
        self.load_cars()

    def closeEvent(self, a0):
        self.closed.emit()
        a0.accept()

    def keyPressEvent(self, a0):
        if a0.key() == Qt.Key.Key_Escape:
            self.close()

    def add_car(self):
        self.add_car_window = admin_windows.AddCarWindow()
        self.add_car_window.show()
        self.add_car_window.closed.connect(lambda: self.load_cars())

    def edit_users(self):
        self.edit_users_window = admin_windows.EditUsersWindow()
        self.edit_users_window.show()

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

    def edit_selected_car(self):
        selected_row = self.ui.table.currentRow()
        conn = sqlite3.connect('cars.sqlite')
        cursor = conn.cursor()
        if selected_row >= 0:
            car_id = selected_row + 1
            cursor.execute(f'SELECT image_path FROM cars WHERE id={car_id}')
            image_path = cursor.fetchone()[0]
            current_data = [
                self.ui.table.item(selected_row, 0).text(),  #Rented
                self.ui.table.item(selected_row, 1).text(),  # Name
                self.ui.table.item(selected_row, 2).text(),  # Brand
                self.ui.table.item(selected_row, 3).text(),  # Year
                self.ui.table.item(selected_row, 4).text(),  # Cost
                self.ui.table.item(selected_row, 5).text(),  # Info
                image_path  # Image
            ]
            print(current_data)
            self.edit_car_window = admin_windows.EditCarWindow(car_id, current_data)
            self.edit_car_window.show()
            self.edit_car_window.closed.connect(lambda: self.load_cars())
        else:
            QMessageBox.warning(self, 'Error', 'Choose a car to edit')
        cursor.close()
        conn.close()

    def delete_selected_car(self):
        selected_row = self.ui.table.currentRow()
        car_id = selected_row + 1
        if car_id is None:
            QMessageBox.warning(None, "Warning", 'Select car')
            return

        conn = sqlite3.connect('cars.sqlite')
        cursor = conn.cursor()

        try:
            cursor.execute(f"DELETE FROM cars WHERE id={car_id}")
            reply = QMessageBox.question(self, 'Confirm', 'Save changes?',
                                         QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                         QMessageBox.StandardButton.No)

            if reply == QMessageBox.StandardButton.Yes:
                conn.commit()
                QMessageBox.information(None, "Success", "Car was deleted")
            else:
                QMessageBox.information(self, 'Exit', 'Changes weren\'t saved')

            self.load_cars()
        except sqlite3.Error as e:
            QMessageBox.critical(None, "Error", f"Couldn\'t delete car': {e}")
        finally:
            cursor.close()
            conn.close()

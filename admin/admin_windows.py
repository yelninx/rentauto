import sqlite3

from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtWidgets import QWidget, QFileDialog, QMessageBox, QTableWidgetItem
import ui_files.ui_add_car
import ui_files.ui_edit_users
import ui_files.ui_edit_user


class EditCarWindow(QWidget):
    closed = pyqtSignal()

    def __init__(self, car_id, current_data):
        super().__init__()
        self.car_id = car_id
        self.current_data = current_data
        self.ui = ui_files.ui_add_car.Ui_Form()
        self.ui.setupUi(self)
        self.ui.rented.setText(current_data[0])
        self.ui.name_input.setText(current_data[1])
        self.ui.brand_input.setText(current_data[2])
        self.ui.year_input.setText(current_data[3])
        self.ui.cost_input.setText(current_data[4])
        self.ui.info_input.setText(current_data[5])
        self.ui.image_input.setText(current_data[6])
        self.ui.browse_image_button.clicked.connect(self.browse_image)
        self.ui.save_button.clicked.connect(self.save_changes)

    def keyPressEvent(self, a0):
        if a0.key() == Qt.Key.Key_Escape:
            self.close()

    def closeEvent(self, event):
        self.closed.emit()
        event.accept()

    def browse_image(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Выберите изображение", "",
                                                   "Images (*.png *.jpg *.jpeg);;All Files (*)")
        if file_path:
            self.ui.image_input.setText(file_path)

    def save_changes(self):
        rented = self.ui.rented.text()
        name = self.ui.name_input.text()
        brand = self.ui.brand_input.text()
        year = self.ui.year_input.text()
        cost = self.ui.cost_input.text()
        info = self.ui.info_input.text()
        image = self.ui.image_input.text()
        conn = sqlite3.connect('cars.sqlite')
        cursor = conn.cursor()
        cursor.execute(
            'UPDATE cars SET is_rented = ?, name = ?, brand = ?, year = ?, cost = ?, info = ?, image_path = ? WHERE id = ?',
            (int(rented), name, brand, int(year), int(cost), info, image, self.car_id))
        reply = QMessageBox.question(self, 'Confirm', 'Save changes?',
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                     QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            conn.commit()
            QMessageBox.information(self, 'Success', 'Changes saved')

        else:
            QMessageBox.information(self, 'Exit', 'Changes weren\'t saved')
        conn.close()
        self.close()


class AddCarWindow(QWidget):
    closed = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.ui = ui_files.ui_add_car.Ui_Form()
        self.ui.setupUi(self)
        self.ui.browse_image_button.clicked.connect(self.browse_image)
        self.ui.save_button.clicked.connect(self.add_car)

    def keyPressEvent(self, a0):
        if a0.key() == Qt.Key.Key_Escape:
            self.close()

    def closeEvent(self, event):
        self.closed.emit()
        event.accept()

    def browse_image(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Выберите изображение", "",
                                                   "Images (*.png *.jpg *.jpeg);;All Files (*)")
        if file_path:
            self.ui.image_input.setText(file_path)

    def add_car(self):
        rented = self.ui.rented.text()
        name = self.ui.name_input.text()
        brand = self.ui.brand_input.text()
        year = self.ui.year_input.text()
        cost = self.ui.cost_input.text()
        image_path = self.ui.image_input.text()
        info = self.ui.info_input.text()

        if name and brand and year.isdigit() and cost:
            conn = sqlite3.connect('cars.sqlite')
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO cars (is_rented, name, brand, year, cost, image_path, info) VALUES (?, ?, ?, ?, ?, ?, ?)',
                (int(rented), name, brand, int(year), int(cost), image_path, info))
            conn.commit()
            conn.close()
            QMessageBox.information(self, 'Success', 'Car added')
            self.close()
        else:
            QMessageBox.warning(self, 'Error', 'Incorrect data')


class EditUsersWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.ui = ui_files.ui_edit_users.Ui_Form()
        self.ui.setupUi(self)
        self.ui.add_button.clicked.connect(self.add_user)
        self.ui.edit_button.clicked.connect(self.edit_user)
        self.ui.delete_button.clicked.connect(self.delete_user)
        self.ui.back_button.clicked.connect(self.back)
        self.load_users()

    def load_users(self):
        conn = sqlite3.connect('cars.sqlite')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users')
        users = cursor.fetchall()
        self.ui.table.setRowCount(len(users))

        for row_index, row_data in enumerate(users):
            self.ui.table.setRowHeight(row_index, 100)
            for column_index, value in enumerate(row_data):
                if column_index != 0:
                    if column_index == 2:
                        continue
                    else:
                        if column_index == 3:
                            self.ui.table.setItem(row_index, column_index - 2, QTableWidgetItem(str(value)))
                        else:
                            self.ui.table.setItem(row_index, column_index - 1, QTableWidgetItem(str(value)))
        conn.close()

    def add_user(self):
        self.add_user_window = AddUser()
        self.add_user_window.show()
        self.add_user_window.closed.connect(lambda: self.load_users())

    def edit_user(self):
        selected_row = self.ui.table.currentRow()
        conn = sqlite3.connect('cars.sqlite')
        cursor = conn.cursor()
        if selected_row >= 0:
            user_id = selected_row + 1
            cursor.execute(f'SELECT password FROM users WHERE id={user_id}')
            password = cursor.fetchone()[0]
            current_data = [
                self.ui.table.item(selected_row, 0).text(),  # Login
                password,
                self.ui.table.item(selected_row, 1).text()
            ]
            print(current_data)
            self.edit_user_window = EditUser(user_id, current_data)
            self.edit_user_window.show()
            self.edit_user_window.closed.connect(lambda: self.load_users())
        else:
            QMessageBox.warning(self, 'Error', 'Choose a user to edit')
        cursor.close()
        conn.close()

    def delete_user(self):
        selected_row = self.ui.table.currentRow()
        user_id = selected_row + 1
        if user_id is None:
            QMessageBox.warning(None, "Warning", 'Select user')
            return

        conn = sqlite3.connect('cars.sqlite')
        cursor = conn.cursor()

        try:
            cursor.execute(f"DELETE FROM users WHERE id={user_id}")
            reply = QMessageBox.question(self, 'Confirm', 'Save changes?',
                                         QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                         QMessageBox.StandardButton.No)

            if reply == QMessageBox.StandardButton.Yes:
                conn.commit()
                QMessageBox.information(None, "Success", "User was deleted")
            else:
                QMessageBox.information(self, 'Exit', 'Changes weren\'t saved')

            self.load_users()
        except sqlite3.Error as e:
            QMessageBox.critical(None, "Error", f"Couldn\'t delete user': {e}")
        finally:
            cursor.close()
            conn.close()

    def back(self):
        self.close()


class EditUser(QWidget):
    closed = pyqtSignal()

    def __init__(self, user_id, data):
        super().__init__()
        self.ui = ui_files.ui_edit_user.Ui_Form()
        self.ui.setupUi(self)
        self.user_id = user_id
        self.data = data
        self.ui.save_button.clicked.connect(self.save_changes)
        self.ui.login_input.setText(self.data[0])
        self.ui.password_input.setText(self.data[1])
        self.ui.is_admin.setChecked(int(self.data[2]))

    def closeEvent(self, event):
        self.closed.emit()
        event.accept()

    def keyPressEvent(self, a0):
        if a0.key() == Qt.Key.Key_Escape:
            self.close()

    def save_changes(self):
        login = self.ui.login_input.text()
        password = self.ui.password_input.text()
        is_admin = 1 if self.ui.is_admin.isChecked() else 0
        conn = sqlite3.connect('cars.sqlite')
        cursor = conn.cursor()
        cursor.execute(
            f'UPDATE users SET login = ?, password = ?, isadmin = ? WHERE id = ?',
            (login, password, is_admin, int(self.user_id)))
        reply = QMessageBox.question(self, 'Confirm', 'Save changes?',
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                     QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            conn.commit()
            QMessageBox.information(self, 'Success', 'Changes saved')

        else:
            QMessageBox.information(self, 'Exit', 'Changes weren\'t saved')
        conn.close()
        self.close()


class AddUser(QWidget):
    closed = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.ui = ui_files.ui_edit_user.Ui_Form()
        self.ui.setupUi(self)
        self.ui.save_button.clicked.connect(self.save_changes)

    def closeEvent(self, event):
        self.closed.emit()
        event.accept()

    def keyPressEvent(self, a0):
        if a0.key() == Qt.Key.Key_Escape:
            self.close()

    def save_changes(self):
        login = self.ui.login_input.text()
        password = self.ui.password_input.text()
        is_admin = 1 if self.ui.is_admin.isChecked() else 0
        print(is_admin)
        if login and password and is_admin.is_integer():
            conn = sqlite3.connect('cars.sqlite')
            cursor = conn.cursor()
            cursor.execute('INSERT INTO users (login, password, isadmin) VALUES (?, ?, ?)',
                           (login, password, is_admin))
            conn.commit()
            conn.close()
            QMessageBox.information(self, 'Success', 'User added')
            self.close()
        else:
            QMessageBox.warning(self, 'Error', 'Incorrect data')

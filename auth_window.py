import sqlite3

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QMessageBox
from ui_files.ui_auth import Ui_Form
import user_mode
from admin import admin_mode


class AuthWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.ui = Ui_Form()
        self.ui.setupUi(self)
        self.ui.login_button.clicked.connect(self.login)
        self.ui.register_button.clicked.connect(self.register)

    def keyPressEvent(self, event):
        if event.key() in (Qt.Key.Key_Enter, Qt.Key.Key_Return):
            self.login()
        if event.key() == Qt.Key.Key_Escape:
            self.close()

    def login(self):
        login = self.ui.login_input.text()
        password = self.ui.password_input.text()
        conn = sqlite3.connect('cars.sqlite')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE login = ? AND password = ?', (login, password))
        user = cursor.fetchone()
        conn.close()
        if user:
            self.open_main_window(user)
        else:
            QMessageBox.warning(self, 'Error', 'Incorrect login or password')

    def register(self):
        login = self.ui.login_input.text()
        password = self.ui.password_input.text()
        conn = sqlite3.connect('cars.sqlite')
        cursor = conn.cursor()
        try:
            cursor.execute('INSERT INTO users (login, password, isadmin) VALUES (?, ?, ?)', (login, password, 0))
            conn.commit()
            QMessageBox.information(self, 'Success', 'Successfuly registered')
        except sqlite3.IntegrityError:
            QMessageBox.warning(self, 'Error', 'Login already registered')
        finally:
            conn.close()

    def temp_hide(self):
        self.ui.login_input.clear()
        self.ui.password_input.clear()
        self.hide()

    def open_main_window(self, user):
        if user[3] == 1:
            self.main_window = admin_mode.MainWindow()
            self.main_window.show()
            self.temp_hide()
            self.main_window.closed.connect(lambda: self.show())
        else:
            self.main_window = user_mode.MainWindow()
            self.main_window.show()
            self.temp_hide()
            self.main_window.closed.connect(lambda: self.show())

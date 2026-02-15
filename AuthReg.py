# AuthReg.py
import sys
import json
from PyQt5.QtWidgets import QApplication, QWidget, QMessageBox
from PyQt5 import uic
from config import Database
import hashlib
import re


class AuthRegForm(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi('AuthReg.ui', self)

        self.db = None
        self.init_database()

        self.admin_window = None

        self.login_button.clicked.connect(self.login)
        self.register_button.clicked.connect(self.register)
        self.show_password_btn.toggled.connect(self.toggle_password_visibility)

        self.register_password.textChanged.connect(self.check_password_strength)
        self.register_confirm_password.textChanged.connect(self.check_password_match)

        self.setWindowTitle("Фермерская информационная система")
        self.login_error_label.clear()
        self.register_error_label.clear()
        self.password_strength_label.clear()

        self.load_saved_credentials()

    def init_database(self):
        try:
            self.db = Database()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка базы данных",
                                 f"Не удалось подключиться к базе данных:\n{str(e)}")
            self.db = None

    def toggle_password_visibility(self, checked):
        echo_mode = self.register_password.Normal if checked else self.register_password.Password
        self.register_password.setEchoMode(echo_mode)
        self.register_confirm_password.setEchoMode(echo_mode)
        self.password_input.setEchoMode(echo_mode)

    def check_password_strength(self):
        password = self.register_password.text()
        if not password:
            self.password_strength_label.setText("")
            return

        errors = []
        if len(password) < 4 or len(password) > 16:
            errors.append("Длина должна быть 4-16 символов")
        if re.search(r'[*&{}|+]', password):
            errors.append("Содержит запрещенные символы (* & { } | +)")
        if not re.search(r'[A-ZА-Я]', password):
            errors.append("Нет заглавных букв")
        if not re.search(r'\d', password):
            errors.append("Нет цифр")

        if errors:
            self.password_strength_label.setText("✗ " + ", ".join(errors))
            self.password_strength_label.setStyleSheet("color: red;")
        else:
            self.password_strength_label.setText("✓ Пароль надежный")
            self.password_strength_label.setStyleSheet("color: green;")

    def check_password_match(self):
        password = self.register_password.text()
        confirm = self.register_confirm_password.text()

        if confirm and password != confirm:
            self.register_error_label.setText("Пароли не совпадают")
            return False
        elif confirm:
            self.register_error_label.setText("")
            return True
        return None

    def save_credentials(self, login, password):
        try:
            with open(".venv/credentials.json", "w") as f:
                json.dump({"login": login, "password": password}, f)
        except:
            pass

    def load_saved_credentials(self):
        try:
            with open(".venv/credentials.json", "r") as f:
                data = json.load(f)
                self.login_input.setText(data.get("login", ""))
                self.password_input.setText(data.get("password", ""))
                self.remember_checkbox.setChecked(True)
        except:
            pass

    def login(self):
        if not self.db:
            QMessageBox.critical(self, "Ошибка", "Нет подключения к БД")
            return

        login = self.login_input.text().strip()
        password = self.password_input.text().strip()
        remember = self.remember_checkbox.isChecked()

        if not login or not password:
            self.login_error_label.setText("Заполните все поля")
            return

        try:
            password_hash = hashlib.sha256(password.encode()).hexdigest()
            query = "SELECT farmer_id, full_name, role FROM farmers WHERE login = %s AND password_hash = %s"
            self.db.cur.execute(query, (login, password_hash))
            user = self.db.cur.fetchone()

            if user:
                if remember:
                    self.save_credentials(login, password)
                else:
                    try:
                        import os
                        if os.path.exists(".venv/credentials.json"):
                            os.remove(".venv/credentials.json")
                    except:
                        pass

                self.current_user = user
                self.hide()

                if user['role'] == 'Администратор':
                    self.open_admin_window()
                else:
                    self.open_user_window()
            else:
                self.login_error_label.setText("Неверный логин или пароль")

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при входе: {str(e)}")

    def register(self):
        if not self.db:
            QMessageBox.critical(self, "Ошибка", "Нет подключения к БД")
            return

        fullname = self.register_fullname.text().strip()
        address = self.register_address.text().strip()
        login = self.register_login.text().strip()
        password = self.register_password.text()
        confirm = self.register_confirm_password.text()
        role = self.user_role.currentText()

        errors = []
        if not fullname:
            errors.append("Укажите ФИО")
        if not login:
            errors.append("Укажите логин")
        if not password:
            errors.append("Укажите пароль")
        if password != confirm:
            errors.append("Пароли не совпадают")

        self.check_password_strength()
        if "✗" in self.password_strength_label.text():
            errors.append("Пароль не соответствует требованиям")

        if errors:
            self.register_error_label.setText("\n".join(errors))
            return

        try:
            self.db.cur.execute("SELECT farmer_id FROM farmers WHERE login = %s", (login,))
            if self.db.cur.fetchone():
                self.register_error_label.setText("Этот логин уже занят")
                return

            password_hash = hashlib.sha256(password.encode()).hexdigest()
            query = """
                INSERT INTO farmers (full_name, address, login, password_hash, role)
                VALUES (%s, %s, %s, %s, %s)
            """
            self.db.cur.execute(query, (fullname, address, login, password_hash, role))
            self.db.con.commit()

            QMessageBox.information(self, "Успех", "Регистрация прошла успешно!")
            self.tabWidget.setCurrentIndex(0)

            self.register_fullname.clear()
            self.register_address.clear()
            self.register_login.clear()
            self.register_password.clear()
            self.register_confirm_password.clear()

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка регистрации: {str(e)}")

    def open_admin_window(self):
        from admin_window import AdminWindow
        try:
            self.admin_window = AdminWindow(self.current_user, self)
            self.admin_window.show()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось открыть панель администратора: {str(e)}")
            self.show()

    def open_user_window(self):
        from admin_window import AdminWindow
        try:
            self.admin_window = AdminWindow(self.current_user, self)
            self.admin_window.show()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось открыть панель пользователя: {str(e)}")
            self.show()

    def show_auth_window(self):
        self.password_input.clear()
        self.show()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AuthRegForm()
    window.show()
    sys.exit(app.exec_())
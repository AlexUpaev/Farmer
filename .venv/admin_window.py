# admin_window.py
import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QMessageBox,
                             QTableWidgetItem, QHeaderView, QInputDialog,
                             QDialog, QVBoxLayout, QFormLayout, QLineEdit,
                             QDialogButtonBox, QLabel, QComboBox)
from PyQt5 import uic
from config import Database


class AdminWindow(QMainWindow):
    def __init__(self, user_info, auth_window):
        super().__init__()
        uic.loadUi('admin_window.ui', self)

        self.user_info = user_info
        self.auth_window = auth_window  # Сохраняем ссылку на окно авторизации
        self.db = Database()

        self.setup_ui()
        self.connect_signals()
        self.load_initial_data()
        self.apply_role_permissions()

        role_title = "Администратор" if user_info['role'] == 'Администратор' else "Фермер"
        self.setWindowTitle(f"{role_title}: {user_info['full_name']}")
        print(f"✓ Окно администратора создано для пользователя: {user_info['full_name']}")

    def setup_ui(self):
        """Настройка интерфейса"""
        # Настройка таблиц
        tables = [self.table_reports, self.table_farmers,
                  self.table_products, self.table_needs]
        for table in tables:
            table.horizontalHeader().setStretchLastSection(True)
            table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
            table.verticalHeader().setVisible(False)

        self.statusbar.showMessage(f"Администратор: {self.user_info['full_name']}")

    def connect_signals(self):
        """Подключение сигналов"""
        print("Подключение сигналов...")

        # Кнопки отчетов
        self.btn_regional_prod.clicked.connect(self.show_regional_production)
        self.btn_farmers_needs.clicked.connect(self.show_farmers_needs)
        self.btn_product_stats.clicked.connect(self.show_product_stats)
        self.btn_farmers_profit.clicked.connect(self.show_farmers_profit)
        self.btn_required_credits.clicked.connect(self.show_required_credits)
        self.btn_credit_profit_diff.clicked.connect(self.show_credit_profit_diff)

        # Поиск
        self.btn_search_product.clicked.connect(self.search_product)
        self.btn_farmer_stats.clicked.connect(self.show_farmer_statistics)

        # Фермеры
        self.btn_add_farmer.clicked.connect(self.add_farmer)
        self.btn_edit_farmer.clicked.connect(self.edit_farmer)
        self.btn_delete_farmer.clicked.connect(self.delete_farmer)
        self.btn_refresh_farmers.clicked.connect(self.load_farmers)
        self.btn_search_farmer.clicked.connect(self.search_farmer)
        self.btn_exit.clicked.connect(self.exit_to_main)

        # Продукция
        self.btn_add_product.clicked.connect(self.add_product)
        self.btn_edit_product.clicked.connect(self.edit_product)
        self.btn_delete_product.clicked.connect(self.delete_product)
        self.btn_filter_products.clicked.connect(self.filter_products)
        self.btn_exit_2.clicked.connect(self.exit_to_main)

        # Потребности
        self.btn_add_need.clicked.connect(self.add_need)
        self.btn_edit_need.clicked.connect(self.edit_need)
        self.btn_delete_need.clicked.connect(self.delete_need)
        self.btn_filter_needs.clicked.connect(self.filter_needs)
        self.btn_exit_3.clicked.connect(self.exit_to_main)

        # Меню
        self.action_exit.triggered.connect(self.exit_to_main)

        print("✓ Сигналы подключены")

    def exit_to_main(self):
        """Выход в главное окно авторизации"""
        reply = QMessageBox.question(self, "Выход",
                                     "Вы уверены, что хотите выйти?\nВы вернетесь на экран авторизации.",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.db.close()
            print("✗ Выход в главное меню")

            # Закрываем окно администратора
            self.close()

            # Показываем окно авторизации
            if self.auth_window:
                self.auth_window.show_auth_window()
            else:
                print("⚠️ Окно авторизации не найдено")

    def load_initial_data(self):
        """Загрузка начальных данных"""
        print("Загрузка начальных данных...")
        try:
            self.load_farmers()
            self.load_products()
            self.load_needs()
            self.load_combo_farmers()

            # Показать отчет по умолчанию
            self.show_regional_production()

            print("✓ Начальные данные загружены")
        except Exception as e:
            print(f"✗ Ошибка загрузки начальных данных: {e}")
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить начальные данные: {str(e)}")

    def load_farmers(self):
        """Загрузка списка фермеров"""
        try:
            print("Загрузка фермеров...")
            farmers = self.db.get_all_farmers()
            print(f"  Получено {len(farmers)} фермеров из БД")

            if farmers and len(farmers) > 0:
                print(f"  Пример первого фермера: {farmers[0]}")

            # Отображаем в таблице
            headers = ["ID", "ФИО", "Адрес", "Телефон", "Логин", "Email", "Дата регистрации", "Роль"]
            count = self.display_in_table(self.table_farmers, farmers, headers)
            print(f"✓ Отображено {count} фермеров в таблице")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка загрузки фермеров: {str(e)}")
            print(f"✗ Ошибка load_farmers: {e}")

    def load_products(self):
        """Загрузка продукции"""
        try:
            print("Загрузка продукции...")
            products = self.db.get_all_products()
            print(f"  Получено {len(products)} записей продукции из БД")

            if products and len(products) > 0:
                print(f"  Пример первой записи продукции: {products[0]}")

            # Правильные заголовки для таблицы products
            headers = ["ID", "Фермер", "Название продукции", "Количество", "Качество",
                       "Цена за ед.", "Дата производства", "Продано", "Себестоимость"]

            count = self.display_in_table(self.table_products, products, headers)
            print(f"✓ Отображено {count} записей продукции в таблице")
        except Exception as e:
            print(f"✗ Ошибка загрузки продукции: {e}")

    def load_needs(self):
        """Загрузка потребностей"""
        try:
            print("Загрузка потребностей...")
            needs = self.db.get_all_needs()
            print(f"  Получено {len(needs)} записей потребностей из БД")

            if needs and len(needs) > 0:
                print(f"  Пример первой записи потребности: {needs[0]}")

            # Правильные заголовки для таблицы needs
            headers = ["ID", "Фермер", "Название потребности", "Тип", "Цена",
                       "Требуемое количество", "Статус", "Дата покупки", "Примечания"]

            count = self.display_in_table(self.table_needs, needs, headers)
            print(f"✓ Отображено {count} записей потребностей в таблице")
        except Exception as e:
            print(f"✗ Ошибка загрузки потребностей: {e}")

    def load_combo_farmers(self):
        """Загрузка фермеров в комбобоксы"""
        try:
            farmers = self.db.get_all_farmers()
            self.combo_farmers.clear()
            self.combo_products_farmer.clear()

            self.combo_farmers.addItem("Все фермеры", 0)
            self.combo_products_farmer.addItem("Все фермеры", 0)

            for farmer in farmers:
                self.combo_farmers.addItem(farmer['full_name'], farmer['farmer_id'])
                self.combo_products_farmer.addItem(farmer['full_name'], farmer['farmer_id'])

            print(f"✓ Загружено {len(farmers)} фермеров в комбобоксы")
        except Exception as e:
            print(f"✗ Ошибка загрузки комбобоксов: {e}")

    def apply_role_permissions(self):
        """Скрываем кнопки управления, если пользователь — не администратор"""
        is_admin = self.user_info.get('role') == 'Администратор'

        # Список всех кнопок, которые должны быть видны ТОЛЬКО админу
        management_buttons = [
            self.btn_add_farmer,
            self.btn_edit_farmer,
            self.btn_delete_farmer,
            self.btn_add_product,
            self.btn_edit_product,
            self.btn_delete_product,
            self.btn_add_need,
            self.btn_edit_need,
            self.btn_delete_need,
        ]

        for btn in management_buttons:
            btn.setVisible(is_admin)

    def display_in_table(self, table, data, headers=None):
        """Отображение данных в таблице"""
        try:
            table.clearContents()
            table.setRowCount(0)

            if not data or len(data) == 0:
                table.setRowCount(1)
                table.setColumnCount(1)
                table.setHorizontalHeaderLabels(["Сообщение"])
                table.setItem(0, 0, QTableWidgetItem("Нет данных для отображения"))
                print(f"  Таблица пуста, показываем сообщение")
                return 0

            print(f"  Отображаем {len(data)} записей в таблице")

            # Автоматически определяем заголовки если не заданы
            if not headers:
                if isinstance(data[0], dict):
                    headers = list(data[0].keys())
                else:
                    headers = [f"Колонка {i + 1}" for i in range(len(data[0]))]

            print(f"  Используем заголовки: {headers}")

            table.setColumnCount(len(headers))
            table.setRowCount(len(data))
            table.setHorizontalHeaderLabels([str(h) for h in headers])

            # Заполняем таблицу
            for row_idx, row_data in enumerate(data):
                for col_idx, header in enumerate(headers):
                    if isinstance(row_data, dict):
                        # Определяем, какой ключ использовать
                        key_to_use = None
                        # Попробуем найти ключ по заголовку (разные возможные имена)
                        possible_keys = [header.lower(), header.replace(" ", "_").lower()]
                        for key in row_data.keys():
                            if key.lower() in possible_keys:
                                key_to_use = key
                                break

                        if key_to_use:
                            value = row_data.get(key_to_use, '')
                        else:
                            # Если ключ не найден, попробуем найти по индексу
                            keys = list(row_data.keys())
                            if col_idx < len(keys):
                                value = row_data[keys[col_idx]]
                            else:
                                value = ''
                    else:
                        # Для списка/кортежа используем индекс
                        value = row_data[col_idx] if col_idx < len(row_data) else ''

                    if value is None:
                        value = ''

                    item = QTableWidgetItem(str(value))
                    table.setItem(row_idx, col_idx, item)

            table.resizeColumnsToContents()
            print(f"  Таблица успешно заполнена")
            return len(data)

        except Exception as e:
            print(f"  Ошибка в display_in_table: {e}")
            import traceback
            traceback.print_exc()
            table.setRowCount(1)
            table.setColumnCount(1)
            table.setItem(0, 0, QTableWidgetItem(f"Ошибка: {str(e)}"))
            return 0

    # ========== ОТЧЕТЫ ==========

    def show_regional_production(self):
        """1. Продукция области"""
        try:
            print("\n" + "=" * 50)
            print("Формирование отчета: Продукция области...")
            data = self.db.get_regional_production()
            print(f"  Получено {len(data) if data else 0} записей")

            if data and len(data) > 0:
                print(f"  Пример первой записи: {data[0]}")

            count = self.display_in_table(self.table_reports, data)
            self.statusbar.showMessage(f"Продукция области: {count} записей")
            print(f"✓ Отчет 'Продукция области': {count} записей")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось получить данные: {str(e)}")
            print(f"✗ Ошибка show_regional_production: {e}")

    def show_farmers_needs(self):
        """2. Потребности фермеров"""
        try:
            print("\n" + "=" * 50)
            print("Формирование отчета: Потребности фермеров...")
            data = self.db.get_farmers_needs()
            print(f"  Получено {len(data) if data else 0} записей")

            if data and len(data) > 0:
                print(f"  Пример первой записи: {data[0]}")

            count = self.display_in_table(self.table_reports, data)
            self.statusbar.showMessage(f"Потребности фермеров: {count} записей")
            print(f"✓ Отчет 'Потребности фермеров': {count} записей")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось получить данные: {str(e)}")
            print(f"✗ Ошибка show_farmers_needs: {e}")

    def show_product_stats(self):
        """3. Производство продукции"""
        product_name, ok = QInputDialog.getText(self, "Поиск продукции",
                                                "Введите название продукции:")
        if ok and product_name:
            try:
                print("\n" + "=" * 50)
                print(f"Поиск продукции: {product_name}")
                data = self.db.get_product_production(product_name)
                print(f"  Получено {len(data) if data else 0} записей")

                if data and len(data) > 0:
                    print(f"  Пример первой записи: {data[0]}")

                count = self.display_in_table(self.table_reports, data)
                self.statusbar.showMessage(f"Продукция '{product_name}': {count} записей")
                print(f"✓ Найдено продукции: {count} записей")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось получить данные: {str(e)}")
                print(f"✗ Ошибка show_product_stats: {e}")
        else:
            print("✗ Пользователь отменил ввод названия продукции")

    def show_farmers_profit(self):
        """4. Прибыль фермеров"""
        try:
            print("\n" + "=" * 50)
            print("Формирование отчета: Прибыль фермеров...")
            data = self.db.calculate_farmers_profit()
            print(f"  Получено {len(data) if data else 0} записей")

            if data and len(data) > 0:
                print(f"  Пример первой записи: {data[0]}")

            count = self.display_in_table(self.table_reports, data)
            self.statusbar.showMessage(f"Прибыль фермеров: {count} записей")
            print(f"✓ Отчет 'Прибыль фермеров': {count} записей")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось получить данные: {str(e)}")
            print(f"✗ Ошибка show_farmers_profit: {e}")

    def show_required_credits(self):
        """5. Требуемые кредиты"""
        try:
            print("\n" + "=" * 50)
            print("Формирование отчета: Требуемые кредиты...")
            data = self.db.calculate_required_credits()
            print(f"  Получено {len(data) if data else 0} записей")

            if data and len(data) > 0:
                print(f"  Пример первой записи: {data[0]}")

            count = self.display_in_table(self.table_reports, data)
            self.statusbar.showMessage(f"Требуемые кредиты: {count} записей")
            print(f"✓ Отчет 'Требуемые кредиты': {count} записей")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось получить данные: {str(e)}")
            print(f"✗ Ошибка show_required_credits: {e}")

    def show_credit_profit_diff(self):
        """6. Разница кредит/прибыль"""
        try:
            print("\n" + "=" * 50)
            print("Формирование отчета: Разница кредит/прибыль...")
            data = self.db.calculate_credit_profit_difference()
            print(f"  Получено {len(data) if data else 0} записей")

            if data and len(data) > 0:
                print(f"  Пример первой записи: {data[0]}")

            count = self.display_in_table(self.table_reports, data)
            self.statusbar.showMessage(f"Разница кредит/прибыль: {count} записей")
            print(f"✓ Отчет 'Разница кредит/прибыль': {count} записей")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось получить данные: {str(e)}")
            print(f"✗ Ошибка show_credit_profit_diff: {e}")

    def search_product(self):
        """Поиск продукции"""
        product_name = self.search_product_input.text()
        if product_name:
            try:
                print("\n" + "=" * 50)
                print(f"Поиск продукции: {product_name}")
                data = self.db.get_product_production(product_name)
                print(f"  Получено {len(data) if data else 0} записей")

                if data and len(data) > 0:
                    print(f"  Пример первой записи: {data[0]}")

                count = self.display_in_table(self.table_reports, data)
                self.statusbar.showMessage(f"Найдено: '{product_name}' - {count} записей")
                print(f"✓ Результаты поиска: {count} записей")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось выполнить поиск: {str(e)}")
                print(f"✗ Ошибка поиска продукции: {e}")
        else:
            QMessageBox.warning(self, "Внимание", "Введите название продукции для поиска")

    def show_farmer_statistics(self):
        """Статистика по фермеру"""
        farmer_id = self.combo_farmers.currentData()
        if farmer_id and farmer_id > 0:
            try:
                farmer_name = self.combo_farmers.currentText()
                print("\n" + "=" * 50)
                print(f"Статистика для фермера: {farmer_name} (ID: {farmer_id})")
                data = self.db.get_farmer_statistics(farmer_id)
                print(f"  Получено {len(data) if data else 0} записей")

                if data and len(data) > 0:
                    print(f"  Пример первой записи: {data[0]}")

                count = self.display_in_table(self.table_reports, data)
                self.statusbar.showMessage(f"Статистика: {farmer_name} - {count} записей")
                print(f"✓ Статистика фермера: {count} записей")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось получить статистику: {str(e)}")
                print(f"✗ Ошибка show_farmer_statistics: {e}")
        else:
            QMessageBox.warning(self, "Внимание", "Выберите фермера из списка")

    # ========== ФЕРМЕРЫ ==========

    def add_farmer(self):
        """Добавление фермера"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Добавить фермера")
        layout = QVBoxLayout()

        form = QFormLayout()
        full_name_input = QLineEdit()
        address_input = QLineEdit()
        phone_input = QLineEdit()
        login_input = QLineEdit()
        password_input = QLineEdit()
        password_input.setEchoMode(QLineEdit.Password)

        form.addRow("ФИО:", full_name_input)
        form.addRow("Адрес:", address_input)
        form.addRow("Телефон:", phone_input)
        form.addRow("Логин:", login_input)
        form.addRow("Пароль:", password_input)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)

        layout.addLayout(form)
        layout.addWidget(buttons)
        dialog.setLayout(layout)

        if dialog.exec_():
            try:
                # Проверка заполнения полей
                if not all([full_name_input.text(), address_input.text(),
                            login_input.text(), password_input.text()]):
                    QMessageBox.warning(self, "Внимание", "Заполните все обязательные поля")
                    return

                # Хешируем пароль
                password_hash = Database.hash_password(password_input.text())

                # Вставляем в БД
                self.db.cur.execute("""
                    INSERT INTO farmers (full_name, address, phone, login, password_hash, role)
                    VALUES (%s, %s, %s, %s, %s, 'Фермер')
                """, (full_name_input.text(), address_input.text(),
                      phone_input.text(), login_input.text(), password_hash))
                self.db.con.commit()

                QMessageBox.information(self, "Успех", "Фермер добавлен")
                print(f"✓ Добавлен новый фермер: {full_name_input.text()}")
                self.load_farmers()
                self.load_combo_farmers()
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Ошибка добавления: {str(e)}")
                print(f"✗ Ошибка добавления фермера: {e}")

    def edit_farmer(self):
        """Редактирование фермера"""
        selected = self.table_farmers.selectedItems()
        if not selected:
            QMessageBox.warning(self, "Внимание", "Выберите фермера для редактирования")
            return

        farmer_id = self.table_farmers.item(selected[0].row(), 0).text()

        try:
            farmer = self.db.get_farmer_by_id(int(farmer_id))
            if not farmer:
                QMessageBox.warning(self, "Ошибка", "Фермер не найден")
                return

            dialog = QDialog(self)
            dialog.setWindowTitle("Редактировать фермера")
            layout = QVBoxLayout()

            form = QFormLayout()
            full_name_input = QLineEdit(farmer['full_name'])
            address_input = QLineEdit(farmer['address'])
            phone_input = QLineEdit(farmer.get('phone', ''))

            form.addRow("ФИО:", full_name_input)
            form.addRow("Адрес:", address_input)
            form.addRow("Телефон:", phone_input)

            buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
            buttons.accepted.connect(dialog.accept)
            buttons.rejected.connect(dialog.reject)

            layout.addLayout(form)
            layout.addWidget(buttons)
            dialog.setLayout(layout)

            if dialog.exec_():
                success = self.db.update_farmer(
                    farmer['farmer_id'],
                    full_name_input.text(),
                    address_input.text(),
                    phone_input.text(),
                    farmer.get('email', '')
                )
                if success:
                    QMessageBox.information(self, "Успех", "Данные обновлены")
                    print(f"✓ Обновлен фермер ID: {farmer_id}")
                    self.load_farmers()
                else:
                    QMessageBox.warning(self, "Ошибка", "Не удалось обновить данные")

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))
            print(f"✗ Ошибка редактирования фермера: {e}")

    def delete_farmer(self):
        """Удаление фермера"""
        selected = self.table_farmers.selectedItems()
        if not selected:
            QMessageBox.warning(self, "Внимание", "Выберите фермера для удаления")
            return

        farmer_name = self.table_farmers.item(selected[0].row(), 1).text()
        farmer_id = self.table_farmers.item(selected[0].row(), 0).text()

        reply = QMessageBox.question(self, "Подтверждение",
                                     f"Удалить фермера '{farmer_name}'?\nВсе связанные данные будут удалены.",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            try:
                success = self.db.delete_farmer(int(farmer_id))
                if success:
                    QMessageBox.information(self, "Успех", "Фермер удален")
                    print(f"✓ Удален фермер ID: {farmer_id}")
                    self.load_farmers()
                    self.load_combo_farmers()
                else:
                    QMessageBox.warning(self, "Ошибка", "Не удалось удалить фермера")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", str(e))
                print(f"✗ Ошибка удаления фермера: {e}")

    def search_farmer(self):
        """Поиск фермера"""
        search_term = self.search_farmer_input.text()
        if search_term:
            try:
                print(f"Поиск фермера: {search_term}")
                data = self.db.search_farmers(search_term)
                headers = ["ID", "ФИО", "Адрес", "Телефон", "Логин"]
                self.display_in_table(self.table_farmers, data, headers)
                self.statusbar.showMessage(f"Найдено фермеров: {len(data)}")
                print(f"✓ Результаты поиска: {len(data)} записей")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", str(e))
                print(f"✗ Ошибка поиска фермера: {e}")
        else:
            self.load_farmers()

    # ========== ПРОДУКЦИЯ И ПОТРЕБНОСТИ ==========

    def add_product(self):
        """Добавление продукции"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Добавить продукцию")
        layout = QVBoxLayout()

        form = QFormLayout()
        farmer_combo = QComboBox()
        product_name_input = QLineEdit()
        quantity_input = QLineEdit()
        quality_input = QLineEdit()
        unit_price_input = QLineEdit()
        production_cost_input = QLineEdit()

        # Заполняем комбобокс фермерами
        farmers = self.db.get_all_farmers()
        for farmer in farmers:
            farmer_combo.addItem(farmer['full_name'], farmer['farmer_id'])

        form.addRow("Фермер:", farmer_combo)
        form.addRow("Название продукции:", product_name_input)
        form.addRow("Количество:", quantity_input)
        form.addRow("Качество:", quality_input)
        form.addRow("Цена за единицу:", unit_price_input)
        form.addRow("Себестоимость:", production_cost_input)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)

        layout.addLayout(form)
        layout.addWidget(buttons)
        dialog.setLayout(layout)

        if dialog.exec_():
            try:
                farmer_id = farmer_combo.currentData()
                if not farmer_id:
                    QMessageBox.warning(self, "Внимание", "Выберите фермера")
                    return

                self.db.cur.execute("""
                    INSERT INTO products (farmer_id, product_name, quantity, quality, 
                                          unit_price, production_cost, production_date)
                    VALUES (%s, %s, %s, %s, %s, %s, CURDATE())
                """, (farmer_id, product_name_input.text(),
                      float(quantity_input.text()) if quantity_input.text() else 0,
                      quality_input.text(),
                      float(unit_price_input.text()) if unit_price_input.text() else 0,
                      float(production_cost_input.text()) if production_cost_input.text() else 0))
                self.db.con.commit()

                QMessageBox.information(self, "Успех", "Продукция добавлена")
                print(f"✓ Добавлена новая продукция: {product_name_input.text()}")
                self.load_products()
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Ошибка добавления: {str(e)}")
                print(f"✗ Ошибка добавления продукции: {e}")

    def edit_product(self):
        """Редактирование продукции"""
        selected = self.table_products.selectedItems()
        if not selected:
            QMessageBox.warning(self, "Внимание", "Выберите продукцию для редактирования")
            return

        product_id = self.table_products.item(selected[0].row(), 0).text()

        try:
            # Получаем данные о продукции
            self.db.cur.execute("SELECT * FROM products WHERE product_id = %s", (product_id,))
            product = self.db.cur.fetchone()

            if not product:
                QMessageBox.warning(self, "Ошибка", "Продукция не найдена")
                return

            dialog = QDialog(self)
            dialog.setWindowTitle("Редактировать продукцию")
            layout = QVBoxLayout()

            form = QFormLayout()
            product_name_input = QLineEdit(product['product_name'])
            quantity_input = QLineEdit(str(product['quantity']))
            quality_input = QLineEdit(product['quality'])
            unit_price_input = QLineEdit(str(product['unit_price']))
            production_cost_input = QLineEdit(str(product['production_cost']))

            form.addRow("Название продукции:", product_name_input)
            form.addRow("Количество:", quantity_input)
            form.addRow("Качество:", quality_input)
            form.addRow("Цена за единицу:", unit_price_input)
            form.addRow("Себестоимость:", production_cost_input)

            buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
            buttons.accepted.connect(dialog.accept)
            buttons.rejected.connect(dialog.reject)

            layout.addLayout(form)
            layout.addWidget(buttons)
            dialog.setLayout(layout)

            if dialog.exec_():
                self.db.cur.execute("""
                    UPDATE products 
                    SET product_name = %s, quantity = %s, quality = %s, 
                        unit_price = %s, production_cost = %s
                    WHERE product_id = %s
                """, (product_name_input.text(),
                      float(quantity_input.text()) if quantity_input.text() else 0,
                      quality_input.text(),
                      float(unit_price_input.text()) if unit_price_input.text() else 0,
                      float(production_cost_input.text()) if production_cost_input.text() else 0,
                      product_id))
                self.db.con.commit()

                QMessageBox.information(self, "Успех", "Продукция обновлена")
                print(f"✓ Обновлена продукция ID: {product_id}")
                self.load_products()

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка редактирования: {str(e)}")
            print(f"✗ Ошибка редактирования продукции: {e}")

    def delete_product(self):
        """Удаление продукции"""
        selected = self.table_products.selectedItems()
        if not selected:
            QMessageBox.warning(self, "Внимание", "Выберите продукцию для удаления")
            return

        product_name = self.table_products.item(selected[0].row(), 2).text()
        product_id = self.table_products.item(selected[0].row(), 0).text()

        reply = QMessageBox.question(self, "Подтверждение",
                                     f"Удалить продукцию '{product_name}'?",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            try:
                self.db.cur.execute("DELETE FROM products WHERE product_id = %s", (product_id,))
                self.db.con.commit()

                QMessageBox.information(self, "Успех", "Продукция удалена")
                print(f"✓ Удалена продукция ID: {product_id}")
                self.load_products()
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Ошибка удаления: {str(e)}")
                print(f"✗ Ошибка удаления продукции: {e}")

    def filter_products(self):
        """Фильтрация продукции"""
        farmer_id = self.combo_products_farmer.currentData()
        if farmer_id:
            try:
                if farmer_id == 0:
                    self.load_products()
                else:
                    products = self.db.get_farmer_products(farmer_id)
                    headers = ["ID", "Название продукции", "Количество", "Качество",
                               "Цена за ед.", "Дата производства", "Продано", "Себестоимость"]
                    self.display_in_table(self.table_products, products, headers)
                    self.statusbar.showMessage(f"Продукция выбранного фермера: {len(products)} записей")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", str(e))
                print(f"✗ Ошибка фильтрации продукции: {e}")

    def add_need(self):
        """Добавление потребности"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Добавить потребность")
        layout = QVBoxLayout()

        form = QFormLayout()
        farmer_combo = QComboBox()
        need_name_input = QLineEdit()
        need_type_combo = QComboBox()
        price_input = QLineEdit()
        quantity_input = QLineEdit()
        status_combo = QComboBox()

        # Заполняем комбобоксы
        farmers = self.db.get_all_farmers()
        for farmer in farmers:
            farmer_combo.addItem(farmer['full_name'], farmer['farmer_id'])

        need_type_combo.addItems(["Товар", "Услуга"])
        status_combo.addItems(["Требуется", "Закуплено", "В процессе"])

        form.addRow("Фермер:", farmer_combo)
        form.addRow("Название потребности:", need_name_input)
        form.addRow("Тип:", need_type_combo)
        form.addRow("Цена:", price_input)
        form.addRow("Требуемое количество:", quantity_input)
        form.addRow("Статус:", status_combo)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)

        layout.addLayout(form)
        layout.addWidget(buttons)
        dialog.setLayout(layout)

        if dialog.exec_():
            try:
                farmer_id = farmer_combo.currentData()
                if not farmer_id:
                    QMessageBox.warning(self, "Внимание", "Выберите фермера")
                    return

                self.db.cur.execute("""
                    INSERT INTO needs (farmer_id, need_name, need_type, price, 
                                       required_quantity, status, purchase_date)
                    VALUES (%s, %s, %s, %s, %s, %s, NULL)
                """, (farmer_id, need_name_input.text(),
                      need_type_combo.currentText(),
                      float(price_input.text()) if price_input.text() else 0,
                      float(quantity_input.text()) if quantity_input.text() else 0,
                      status_combo.currentText()))
                self.db.con.commit()

                QMessageBox.information(self, "Успех", "Потребность добавлена")
                print(f"✓ Добавлена новая потребность: {need_name_input.text()}")
                self.load_needs()
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Ошибка добавления: {str(e)}")
                print(f"✗ Ошибка добавления потребности: {e}")

    def edit_need(self):
        """Редактирование потребности"""
        selected = self.table_needs.selectedItems()
        if not selected:
            QMessageBox.warning(self, "Внимание", "Выберите потребность для редактирования")
            return

        need_id = self.table_needs.item(selected[0].row(), 0).text()

        try:
            # Получаем данные о потребности
            self.db.cur.execute("SELECT * FROM needs WHERE need_id = %s", (need_id,))
            need = self.db.cur.fetchone()

            if not need:
                QMessageBox.warning(self, "Ошибка", "Потребность не найдена")
                return

            dialog = QDialog(self)
            dialog.setWindowTitle("Редактировать потребность")
            layout = QVBoxLayout()

            form = QFormLayout()
            need_name_input = QLineEdit(need['need_name'])
            need_type_combo = QComboBox()
            price_input = QLineEdit(str(need['price']))
            quantity_input = QLineEdit(str(need['required_quantity']))
            status_combo = QComboBox()

            need_type_combo.addItems(["Товар", "Услуга"])
            status_combo.addItems(["Требуется", "Закуплено", "В процессе"])

            # Устанавливаем текущие значения
            need_type_combo.setCurrentText(need['need_type'])
            status_combo.setCurrentText(need['status'])

            form.addRow("Название потребности:", need_name_input)
            form.addRow("Тип:", need_type_combo)
            form.addRow("Цена:", price_input)
            form.addRow("Требуемое количество:", quantity_input)
            form.addRow("Статус:", status_combo)

            buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
            buttons.accepted.connect(dialog.accept)
            buttons.rejected.connect(dialog.reject)

            layout.addLayout(form)
            layout.addWidget(buttons)
            dialog.setLayout(layout)

            if dialog.exec_():
                self.db.cur.execute("""
                    UPDATE needs 
                    SET need_name = %s, need_type = %s, price = %s, 
                        required_quantity = %s, status = %s
                    WHERE need_id = %s
                """, (need_name_input.text(),
                      need_type_combo.currentText(),
                      float(price_input.text()) if price_input.text() else 0,
                      float(quantity_input.text()) if quantity_input.text() else 0,
                      status_combo.currentText(),
                      need_id))
                self.db.con.commit()

                QMessageBox.information(self, "Успех", "Потребность обновлена")
                print(f"✓ Обновлена потребность ID: {need_id}")
                self.load_needs()

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка редактирования: {str(e)}")
            print(f"✗ Ошибка редактирования потребности: {e}")

    def delete_need(self):
        """Удаление потребности"""
        selected = self.table_needs.selectedItems()
        if not selected:
            QMessageBox.warning(self, "Внимание", "Выберите потребность для удаления")
            return

        need_name = self.table_needs.item(selected[0].row(), 2).text()
        need_id = self.table_needs.item(selected[0].row(), 0).text()

        reply = QMessageBox.question(self, "Подтверждение",
                                     f"Удалить потребность '{need_name}'?",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            try:
                self.db.cur.execute("DELETE FROM needs WHERE need_id = %s", (need_id,))
                self.db.con.commit()

                QMessageBox.information(self, "Успех", "Потребность удалена")
                print(f"✓ Удалена потребность ID: {need_id}")
                self.load_needs()
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Ошибка удаления: {str(e)}")
                print(f"✗ Ошибка удаления потребности: {e}")

    def filter_needs(self):
        """Фильтрация потребностей"""
        status = self.combo_need_status.currentText()
        if status != "Все":
            try:
                needs = self.db.get_all_needs()
                filtered = [n for n in needs if n.get('status') == status]
                headers = ["ID", "Фермер", "Название потребности", "Тип", "Цена",
                           "Требуемое количество", "Статус", "Дата покупки", "Примечания"]
                self.display_in_table(self.table_needs, filtered, headers)
                self.statusbar.showMessage(f"Потребности со статусом '{status}': {len(filtered)} записей")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", str(e))
                print(f"✗ Ошибка фильтрации потребностей: {e}")
        else:
            self.load_needs()

    # ========== ДОПОЛНИТЕЛЬНЫЕ МЕТОДЫ ==========

    def closeEvent(self, event):
        """Обработка закрытия окна"""
        reply = QMessageBox.question(self, "Выход",
                                     "Вы уверены, что хотите выйти?",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.db.close()
            print("✗ Окно администратора закрыто")

            # Показываем окно авторизации при закрытии
            if self.auth_window:
                self.auth_window.show_auth_window()

            event.accept()
        else:
            event.ignore()


# Тестовый запуск (если запускается напрямую, а не из main.py)
if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Тестовые данные пользователя (для тестирования без авторизации)
    test_user = {
        'farmer_id': 1,
        'full_name': 'Администратор системы (тест)',
        'role': 'Администратор'
    }


    # Для теста создаем фиктивное окно авторизации
    class FakeAuthWindow:
        def show_auth_window(self):
            print("Тест: Показано окно авторизации")


    window = AdminWindow(test_user, FakeAuthWindow())
    window.show()
    sys.exit(app.exec_())
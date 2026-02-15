# config.py
from mysql.connector import connect, Error
import hashlib


class Database:
    """Класс для работы с базой данных фермерской информационной системы"""

    def __init__(self):
        self.connect_to_database()

    def connect_to_database(self):
        """Установка соединения с базой данных MySQL"""
        try:
            self.con = connect(
                user="root",
                host="localhost",
                database="farmer_db",
                password="root",
                ssl_disabled=True
            )
            self.cur = self.con.cursor(dictionary=True)
        except Error as e:
            raise Exception(f"Ошибка подключения к БД: {e}")

    def close(self):
        """Закрытие соединения с базой данных"""
        if self.con and self.con.is_connected():
            self.cur.close()
            self.con.close()

    @staticmethod
    def hash_password(password):
        """Хеширование пароля с использованием SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()

    def clear_unread_results(self):
        """Очистка непрочитанных результатов запроса (для предотвращения ошибок)"""
        try:
            while self.cur.nextset():
                pass
        except:
            pass

    # ========== ОТЧЕТЫ ==========

    def get_regional_production(self):
        """1. Продукция, производимая фермерами области"""
        try:
            self.clear_unread_results()
            self.cur.execute("""
                SELECT 
                    p.product_id,
                    f.full_name as farmer_name,
                    p.product_name,
                    p.quantity,
                    p.quality,
                    p.unit_price as price,
                    p.production_date,
                    p.sold_quantity,
                    p.production_cost,
                    (p.quantity * p.unit_price) as total_value
                FROM products p
                JOIN farmers f ON p.farmer_id = f.farmer_id
                WHERE f.role != 'Администратор'
                ORDER BY p.production_date DESC
            """)
            return self.cur.fetchall()
        except Error:
            return []

    def get_farmers_needs(self):
        """2. Потребности фермеров для производства"""
        try:
            self.clear_unread_results()
            self.cur.execute("""
                SELECT 
                    n.need_id,
                    f.full_name as farmer_name,
                    n.need_name,
                    n.need_type as type,
                    n.price,
                    n.required_quantity,
                    n.status,
                    n.purchase_date,
                    n.notes
                FROM needs n
                JOIN farmers f ON n.farmer_id = f.farmer_id
                WHERE f.role != 'Администратор'
                ORDER BY n.need_id DESC
            """)
            return self.cur.fetchall()
        except Error:
            return []

    def get_product_production(self, product_name):
        """3. Количество заданной продукции, производимой фермерами"""
        try:
            self.clear_unread_results()
            self.cur.execute("""
                SELECT 
                    p.product_id,
                    f.full_name as farmer_name,
                    p.product_name,
                    p.quantity,
                    p.quality,
                    p.unit_price as price,
                    p.production_date,
                    (p.quantity * p.unit_price) as total_value
                FROM products p
                JOIN farmers f ON p.farmer_id = f.farmer_id
                WHERE p.product_name LIKE %s 
                AND f.role != 'Администратор'
                ORDER BY p.quantity DESC
            """, (f"%{product_name}%",))
            return self.cur.fetchall()
        except Error:
            return []

    def calculate_farmers_profit(self):
        """4. Прибыль фермеров по каждому виду продукции"""
        try:
            self.clear_unread_results()
            self.cur.execute("""
                SELECT 
                    f.full_name as farmer_name,
                    p.product_name,
                    p.quantity,
                    p.unit_price as price_per_unit,
                    p.production_cost as cost_per_unit,
                    (p.quantity * p.unit_price) as total_revenue,
                    (p.quantity * p.production_cost) as total_cost,
                    (p.quantity * (p.unit_price - p.production_cost)) as profit
                FROM products p
                JOIN farmers f ON p.farmer_id = f.farmer_id
                WHERE f.role != 'Администратор'
                ORDER BY profit DESC
            """)
            return self.cur.fetchall()
        except Error:
            return []

    def calculate_required_credits(self):
        """5. Требуемый кредит для каждого фермера"""
        try:
            self.clear_unread_results()
            self.cur.execute("""
                SELECT 
                    f.full_name as farmer_name,
                    SUM(n.price * n.required_quantity) as total_credit_needed,
                    COUNT(n.need_id) as needs_count,
                    GROUP_CONCAT(n.need_name SEPARATOR ', ') as needs_list
                FROM needs n
                JOIN farmers f ON n.farmer_id = f.farmer_id
                WHERE f.role != 'Администратор' 
                AND n.status IN ('Требуется', 'В процессе')
                GROUP BY f.farmer_id, f.full_name
                ORDER BY total_credit_needed DESC
            """)
            return self.cur.fetchall()
        except Error:
            return []

    def calculate_credit_profit_difference(self):
        """6. Разница между кредитом и полученной прибылью"""
        try:
            self.clear_unread_results()
            self.cur.execute("""
                SELECT 
                    f.farmer_id,
                    f.full_name as farmer_name,
                    SUM(p.quantity * (p.unit_price - p.production_cost)) as total_profit
                FROM products p
                JOIN farmers f ON p.farmer_id = f.farmer_id
                WHERE f.role != 'Администратор'
                GROUP BY f.farmer_id, f.full_name
            """)
            profits = self.cur.fetchall()

            self.clear_unread_results()
            self.cur.execute("""
                SELECT 
                    f.farmer_id,
                    f.full_name as farmer_name,
                    SUM(n.price * n.required_quantity) as total_credit_needed
                FROM needs n
                JOIN farmers f ON n.farmer_id = f.farmer_id
                WHERE f.role != 'Администратор' 
                AND n.status IN ('Требуется', 'В процессе')
                GROUP BY f.farmer_id, f.full_name
            """)
            credits = self.cur.fetchall()

            result = []
            for profit in profits:
                farmer_id = profit['farmer_id']
                credit_info = next((c for c in credits if c['farmer_id'] == farmer_id), None)
                total_credit = credit_info['total_credit_needed'] if credit_info else 0
                total_profit = profit['total_profit'] or 0
                difference = total_profit - total_credit

                result.append({
                    'farmer_name': profit['farmer_name'],
                    'total_profit': total_profit,
                    'total_credit_needed': total_credit,
                    'difference': difference,
                    'status': 'Прибыль > Кредит' if difference > 0 else 'Кредит > Прибыль' if difference < 0 else 'Равны'
                })
            return result
        except Error:
            return []

    def get_farmer_statistics(self, farmer_id):
        """7. Статистика по конкретному фермеру"""
        try:
            self.clear_unread_results()
            self.cur.execute("SELECT * FROM farmers WHERE farmer_id = %s", (farmer_id,))
            farmer = self.cur.fetchone()

            self.clear_unread_results()
            self.cur.execute("""
                SELECT 
                    product_name,
                    SUM(quantity) as total_quantity,
                    AVG(unit_price) as avg_price,
                    SUM(quantity * unit_price) as total_value
                FROM products 
                WHERE farmer_id = %s
                GROUP BY product_name
            """, (farmer_id,))
            products_stats = self.cur.fetchall()

            self.clear_unread_results()
            self.cur.execute("""
                SELECT 
                    status,
                    COUNT(*) as count,
                    SUM(price * required_quantity) as total_cost
                FROM needs 
                WHERE farmer_id = %s
                GROUP BY status
            """, (farmer_id,))
            needs_stats = self.cur.fetchall()

            result = [{
                'farmer_id': farmer_id,
                'full_name': farmer['full_name'] if farmer else 'Не найден',
                'address': farmer['address'] if farmer else '',
                'total_products': len(products_stats),
                'total_needs': sum(item['count'] for item in needs_stats),
                'products_value': sum(item['total_value'] for item in products_stats) if products_stats else 0,
                'needs_cost': sum(item['total_cost'] for item in needs_stats) if needs_stats else 0
            }]

            for product in products_stats:
                result.append({
                    'type': 'Продукция',
                    'название': product['product_name'],
                    'общее_количество': product['total_quantity'],
                    'средняя_цена': product['avg_price'],
                    'общая_стоимость': product['total_value']
                })

            for need in needs_stats:
                result.append({
                    'type': 'Потребность',
                    'статус': need['status'],
                    'количество': need['count'],
                    'общая_стоимость': need['total_cost']
                })
            return result
        except Error:
            return []

    # ========== УПРАВЛЕНИЕ ДАННЫМИ ==========

    def get_all_farmers(self):
        """Получение списка всех фермеров (исключая администраторов)"""
        try:
            self.clear_unread_results()
            self.cur.execute("""
                SELECT farmer_id, full_name, address, phone, login, email, 
                       created_at as registration_date, role
                FROM farmers 
                WHERE role != 'Администратор'
                ORDER BY farmer_id
            """)
            return self.cur.fetchall()
        except Error:
            return []

    def search_farmers(self, search_term):
        """Поиск фермеров по ФИО, адресу или логину"""
        try:
            self.clear_unread_results()
            self.cur.execute("""
                SELECT farmer_id, full_name, address, phone, login
                FROM farmers 
                WHERE (full_name LIKE %s OR address LIKE %s OR login LIKE %s)
                AND role != 'Администратор'
            """, (f"%{search_term}%", f"%{search_term}%", f"%{search_term}%"))
            return self.cur.fetchall()
        except Error:
            return []

    def get_farmer_by_id(self, farmer_id):
        """Получение данных фермера по ID"""
        try:
            self.clear_unread_results()
            self.cur.execute("SELECT * FROM farmers WHERE farmer_id = %s", (farmer_id,))
            return self.cur.fetchone()
        except Error:
            return None

    def update_farmer(self, farmer_id, full_name, address, phone, email):
        """Обновление данных фермера"""
        try:
            self.clear_unread_results()
            self.cur.execute("""
                UPDATE farmers 
                SET full_name = %s, address = %s, phone = %s, email = %s 
                WHERE farmer_id = %s
            """, (full_name, address, phone, email, farmer_id))
            self.con.commit()
            return self.cur.rowcount > 0
        except Error:
            self.con.rollback()
            return False

    def delete_farmer(self, farmer_id):
        """Удаление фермера и связанных данных"""
        try:
            self.clear_unread_results()
            self.cur.execute("DELETE FROM farmers WHERE farmer_id = %s", (farmer_id,))
            self.con.commit()
            return self.cur.rowcount > 0
        except Error:
            self.con.rollback()
            return False

    def get_farmer_products(self, farmer_id):
        """Получение продукции конкретного фермера"""
        try:
            self.clear_unread_results()
            self.cur.execute("SELECT * FROM products WHERE farmer_id = %s", (farmer_id,))
            return self.cur.fetchall()
        except Error:
            return []

    def get_farmer_needs(self, farmer_id):
        """Получение потребностей конкретного фермера"""
        try:
            self.clear_unread_results()
            self.cur.execute("SELECT * FROM needs WHERE farmer_id = %s", (farmer_id,))
            return self.cur.fetchall()
        except Error:
            return []

    def get_all_products(self):
        """Получение всей продукции всех фермеров"""
        try:
            self.clear_unread_results()
            self.cur.execute("""
                SELECT p.*, f.full_name 
                FROM products p 
                LEFT JOIN farmers f ON p.farmer_id = f.farmer_id
                ORDER BY p.product_id DESC
            """)
            return self.cur.fetchall()
        except Error:
            return []

    def get_all_needs(self):
        """Получение всех потребностей всех фермеров"""
        try:
            self.clear_unread_results()
            self.cur.execute("""
                SELECT 
                    n.need_id,
                    n.farmer_id,
                    n.need_name,
                    n.need_type as type,
                    n.price,
                    n.required_quantity as quantity,
                    n.status,
                    n.purchase_date,
                    n.notes,
                    f.full_name 
                FROM needs n 
                LEFT JOIN farmers f ON n.farmer_id = f.farmer_id
                ORDER BY n.need_id DESC
            """)
            return self.cur.fetchall()
        except Error:
            return []
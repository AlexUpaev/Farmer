# test_db.py
"""Тестирование функционала работы с базой данных фермерской информационной системы"""

from config import Database


def test_procedures():
    """Тестирование основных запросов к базе данных"""
    db = Database()

    try:
        print("1. Региональное производство:")
        result = db.get_regional_production()
        for row in result[:3]:
            print(f"  {row.get('farmer_name', 'N/A')}: {row.get('product_name', 'N/A')} - "
                  f"{row.get('quantity', 0)} ед., стоимость: {row.get('total_value', 0):.2f} руб.")

        print("\n2. Прибыль фермеров:")
        result = db.calculate_farmers_profit()
        for row in result[:3]:
            profit = row.get('profit', 0)
            print(f"  {row.get('farmer_name', 'N/A')}: {row.get('product_name', 'N/A')} - "
                  f"прибыль: {profit:.2f} руб.")

        print("\n3. Требуемые кредиты:")
        result = db.calculate_required_credits()
        for row in result[:3]:
            credit = row.get('total_credit_needed', 0)
            print(f"  {row.get('farmer_name', 'N/A')}: требуется {credit:.2f} руб. "
                  f"({row.get('needs_count', 0)} потребностей)")

        print("\n4. Список фермеров:")
        result = db.get_all_farmers()
        for row in result[:5]:
            print(f"  ID: {row['farmer_id']}, ФИО: {row['full_name']}, Роль: {row['role']}")

        print("\n✅ Тестирование успешно завершено")

    except Exception as e:
        print(f"❌ Ошибка при тестировании: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    test_procedures()
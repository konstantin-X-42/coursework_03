import os
from dotenv import load_dotenv

from src.api import APIAdapter
from src.db_manager import DBManager
from src.models import Aeroplane

# Загружаем переменные окружения из файла .env
load_dotenv()

# Список из 10 стран для обязательного мониторинга
LISTED_COUNTRIES = [
    "Canada", "USA", "France", "Germany", "Russia",
    "United Kingdom", "China", "Japan", "Australia", "Brazil"
]

# Безопасное получение параметров из переменных окружения (.env)
# Если переменная не найдена, подставляется безопасное дефолтное значение
DB_PARAMS = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", 5432)),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", ""),
    "database": os.getenv("DB_NAME", "coursework_03_db")
}


def bootstrap_database(api: APIAdapter, db: DBManager) -> None:
    """Автоматически обходит 10 стран из ТЗ, собирает данные через API и заполняет БД."""
    print("\n🔄 Инициализация базы данных...")
    print("🗑️ Очистка старых данных перед новой загрузкой...")
    db.clear_tables()

    for country in LISTED_COUNTRIES:
        print(f"📡 Запрос данных для страны: {country}...")
        api.get_aeroplanes(country)

        planes_objects = []
        if api.aeroplanes and "states" in api.aeroplanes and api.aeroplanes["states"]:
            raw_planes = api.aeroplanes["states"]

            for p in raw_planes:
                # Безопасно извлекаем данные, проверяя длину списка ответа API
                velocity = p[9] if len(p) > 9 else None
                altitude = p[7] if len(p) > 7 else None

                plane_obj = Aeroplane(
                    callsign=p[1],
                    origin_country=p[2],
                    velocity=velocity,
                    altitude=altitude
                )
                planes_objects.append(plane_obj)

            db.save_aeroplanes_data(country, planes_objects)
            print(f"✅ Успешно сохранено самолетов: {len(planes_objects)}")
        else:
            print(f"ℹ️ В воздушном пространстве {country} сейчас нет активных самолетов (или включен демо-режим).")

    print("\n✨ База данных успешно заполнена и готова к аналитике!")


def user_interaction() -> None:
    """Функция для интерактивного взаимодействия с пользователем через консольное меню."""
    api = APIAdapter()
    db = DBManager(db_params=DB_PARAMS)

    print("====================================================")
    print("🛫  СИСТЕМА АНАЛИТИКИ ВОЗДУШНОГО ПРОСТРАНСТВА (БД)  🛬")
    print("====================================================")

    # Автоматическое первичное наполнение таблиц по 10 странам
    bootstrap_database(api, db)

    while True:
        print("\n" + "=" * 50)
        print("  ГЛАВНОЕ АНАЛИТИЧЕСКОЕ МЕНЮ (PostgreSQL):")
        print("=" * 50)
        print("1. Количество самолетов по странам (JOIN)")
        print("2. Показать список всех воздушных судов")
        print("3. Получить среднюю скорость всех самолетов (AVG)")
        print("4. Самолеты со скоростью выше средней")
        print("5. Поиск самолетов по ключевым словам в позывном")
        print("6. Выйти из программы")
        print("=" * 50)

        choice = input("👉 Выберите пункт меню (1-6): ").strip()

        if choice == "1":
            print("\n📊 КОЛИЧЕСТВО САМОЛЕТОВ В ВОЗДУШНОМ ПРОСТРАНСТВЕ СТРАН:")
            data = db.get_countries_and_aeroplanes_count()
            for idx, item in enumerate(data, 1):
                print(f"{idx}. Страна: {item['country']:<15} | Самолетов в небе: {item['aeroplanes_count']}")

        elif choice == "2":
            print("\n✈️ ПОЛНЫЙ СПИСОК ВСЕХ ВОЗДУШНЫХ СУДОВ В БАЗЕ:")
            data = db.get_all_aeroplanes()
            if not data:
                print("❌ База данных пуста.")
                continue
            for idx, item in enumerate(data, 1):
                print(
                    f"{idx}. Позывной: {item['callsign']:<9} | "
                    f"Страна: {item['origin_country']:<15} | "
                    f"Скорость: {float(item['velocity']):.1f} м/с | "
                    f"Высота: {float(item['altitude']):.1f} м"
                )

        elif choice == "3":
            avg_speed = db.get_avg_speed()
            print(f"\n📈 СРЕДНЯЯ СКОРОСТЬ ВСЕХ САМОЛЕТОВ В БАЗЕ: {avg_speed:.2f} м/с")

        elif choice == "4":
            print("\n🚀 САМОЛЕТЫ, ЛЕТЯЩИЕ БЫСТРЕЕ СРЕДНЕЙ СКОРОСТИ:")
            data = db.get_aeroplanes_with_higher_speed()
            if not data:
                print("ℹ️ Нет самолетов со скоростью выше средней (или в базе всего 1 самолет).")
                continue
            for idx, item in enumerate(data, 1):
                print(
                    f"{idx}. {item['callsign']:<9} | "
                    f"Скорость: {float(item['velocity']):.1f} м/с "
                    f"(Регистрация: {item['origin_country']})"
                )

        elif choice == "5":
            keyword = input("🔍 Введите часть позывного для поиска (например, ACA): ").strip()
            if not keyword:
                print("❌ Ключевое слово не может быть пустым.")
                continue

            print(f"\n🔎 РЕЗУЛЬТАТЫ ПОИСКА ДЛЯ КЛЮЧЕВОГО СЛОВА '{keyword.upper()}':")
            data = db.get_aeroplanes_with_keyword(keyword)
            if not data:
                print(f"❌ Самолетов с подстрокой '{keyword.upper()}' в позывном не найдено.")
                continue
            for item in data:
                print(
                    f"• Позывной: {item['callsign']:<9} | "
                    f"Страна: {item['origin_country']:<15} | "
                    f"Высота: {float(item['altitude']):.1f} м"
                )

        elif choice == "6":
            print("\n👋 Программа успешно завершена. Все аналитические данные сохранены в PostgreSQL!")
            break
        else:
            print("❌ Неверный пункт меню. Пожалуйста, выберите число от 1 до 6.")


def main() -> None:
    """Главная точка входа в приложение."""
    user_interaction()


if __name__ == "__main__":
    main()

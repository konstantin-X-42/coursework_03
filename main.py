from src.api import APIAdapter
from src.models import Aeroplane
from src.storage import JsonFileStorage

# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Запуск всех тестов проекта
# poetry run pytest
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# запуск всех тестов в проекте с покрытием html
# poetry run pytest --cov=. --cov-report=html
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


def user_interaction():
    """Функция для взаимодействия с пользователем через консоль (Шаг 4)."""
    api = APIAdapter()
    storage = JsonFileStorage()

    print("====================================================")
    print("🛫  ДОБРО ПОЖАЛОВАТЬ В СИСТЕМУ МОНИТОРИНГА АВИАРЕЙСОВ 🛬")
    print("====================================================")

    # 1. Первый обязательный шаг: запрос данных по стране
    target_country = input(
        "👉 Введите название страны на английском (например, Canada): "
    ).strip()

    print(f"\n[Запрос] Поиск самолетов для страны: {target_country}...")
    api.get_aeroplanes(target_country)

    # Загружаем полученные данные в список объектов Aeroplane и сохраняем в файл
    aeroplanes_objects = []
    if (
        api.aeroplanes
        and "states" in api.aeroplanes
        and api.aeroplanes["states"] is not None
    ):
        raw_planes = api.aeroplanes["states"]
        # ОЧИЩАЕМ СТАРЫЕ ДАННЫЕ ПЕРЕД НОВОЙ ЗАГРУЗКОЙ
        storage.clear_storage()

        for p in raw_planes:
            plane_obj = Aeroplane(
                callsign=p[1],  # Индекс 1 — Позывной (например, "ACA123")
                origin_country=p[2],  # Индекс 2 — Страна регистрации ("Canada")
                velocity=p[9],  # Индекс 9 — Скорость
                altitude=p[7],  # Индекс 7 — Высота
            )
            storage.add_aeroplane(plane_obj)
            aeroplanes_objects.append(plane_obj)

        print(
            f"✅ Данные успешно обновлены. Загружено объектов: {len(aeroplanes_objects)}"
        )
    else:
        print(
            "❌ В этой зоне сейчас нет активных самолетов. Работаем с ранее сохраненной базой."
        )

    # 2. Основной цикл интерактивного меню
    while True:
        print("\n" + "=" * 40)
        print("  ГЛАВНОЕ МЕНЮ ПРОГРАММЫ:")
        print("=" * 40)
        print("1. Показать все самолеты в зоне")
        print("2. Получить ТОП-N самолетов по высоте полета")
        print("3. Найти самолеты по конкретной стране регистрации")
        print("4. Удалить самолет из локальной базы по позывному")
        print("5. Выйти из программы")
        print("=" * 40)

        choice = input("👉 Выберите пункт меню (1-5): ").strip()

        # Перечитываем актуальные данные из JSON для точности
        current_data = storage.get_aeroplanes()
        planes_list = [
            Aeroplane(p["callsign"], p["origin_country"], p["velocity"], p["altitude"])
            for p in current_data
        ]

        if choice == "1":
            print(f"\n✈️ Всего самолетов в базе: {len(planes_list)}")
            for idx, plane in enumerate(planes_list, 1):
                print(
                    f"{idx}. Позывной: {plane.callsign:<8} | Страна рег.: {plane.origin_country:<10} | Высота: {plane.altitude} м | Скорость: {plane.velocity} м/с"
                )

        elif choice == "2":
            if not planes_list:
                print("❌ База данных пуста.")
                continue

            try:
                n = int(
                    input(
                        f"✈️ Сколько самолетов вывести в ТОП? (Доступно {len(planes_list)}): "
                    ).strip()
                )
                if n <= 0:
                    print("❌ Число должно быть больше нуля.")
                    continue

                # Используем встроенный метод сортировки. Так как мы настроили методы __lt__ и __gt__ в Шаге 2,
                # Python может сортировать объекты. Отсортируем по высоте явно через lambda:
                sorted_by_alt = sorted(
                    planes_list, key=lambda x: x.altitude, reverse=True
                )

                print(
                    f"\n✈️ ТОП-{min(n, len(sorted_by_alt))} САМОЛЕТОВ ПО ВЫСОТЕ ПОЛЕТА:"
                )
                for idx, plane in enumerate(sorted_by_alt[:n], 1):
                    print(
                        f"✈️ {idx}. {plane.callsign:<8} -> Высота: {plane.altitude} м (Скорость: {plane.velocity} м/с)"
                    )
            except ValueError:
                print("❌ Пожалуйста, введите корректное целое число.")

        elif choice == "3":
            search_country = (
                input(
                    "🔍 Введите название страны регистрации для поиска (например, Canada): "
                )
                .strip()
                .lower()
            )
            filtered = [
                p for p in planes_list if p.origin_country.lower() == search_country
            ]

            if filtered:
                print(
                    f"\n✈️ Найденные самолеты, зарегистрированные в {search_country.capitalize()}:"
                )
                for plane in filtered:
                    print(
                        f"• Позывной: {plane.callsign:<8} | Высота: {plane.altitude} м | Скорость: {plane.velocity} м/с"
                    )
            else:
                print(
                    f"ℹ❌ Самолётов со страной регистрации '{search_country.capitalize()}' не найдено."
                )

        elif choice == "4":
            callsign_to_del = input(
                "🗑️ Введите позывной самолета для удаления: "
            ).strip()
            storage.delete_aeroplanes_by_callsign(callsign_to_del)

        elif choice == "5":
            print("\n   Программа мониторинга авиарейсов ✈️ успешно завершена. Спасибо за использование!")
            break
        else:
            print("❌ Неверный пункт меню. Попробуйте еще раз.")


def main():
    user_interaction()


if __name__ == "__main__":
    main()

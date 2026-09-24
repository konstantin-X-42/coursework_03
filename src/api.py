import random
from abc import ABC, abstractmethod

from requests import get

# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# запустить модуль api.py через командную строку
# poetry run python api.py
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

# =====================================================================
# 1. АБСТРАКТНЫЙ КЛАСС ДЛЯ РАБОТЫ С API (Шаг 1)
# =====================================================================
class BaseAPIAdapter(ABC):

    @abstractmethod
    def get_aeroplanes(self, country: str) -> None:
        """
        Абстрактный метод для подключения к API, получения координат
        и сбора информации о самолетах в воздушном пространстве страны.
        """
        pass


# =====================================================================
# 2. РЕАЛИЗАЦИЯ КЛАССА-НАСЛЕДНИКА (Шаг 1)
# =====================================================================
class APIAdapter(BaseAPIAdapter):

    def __init__(self) -> None:
        self.openstreetmap_url = "https://nominatim.openstreetmap.org/search"
        self.opensky_url = "https://opensky-network.org/api/states/all"
        self.aeroplanes = None
        # Флаг режима работы
        self.offline_mode = False

        # Локальный справочник координат стран на случай сбоя внешних API
        self._fallback_bounds = {
            "canada": ["41.67", "83.11", "-141.00", "-52.62"],
            "usa": ["24.39", "49.38", "-124.84", "-66.95"],
            "france": ["41.36", "51.10", "-5.14", "9.56"],
            "germany": ["47.27", "55.05", "5.86", "15.04"],
            "russia": ["41.18", "81.85", "19.63", "180.00"],
        }

    def get_aeroplanes(self, country: str) -> None:
        """Получение самолетов"""

        country_clean = country.strip().lower()

        geo_coordinates = None

        geo_source = None

        # =============================================================
        # 1. Получаем координаты через Nominatim
        # =============================================================

        random_id = random.randint(1000, 9999)

        headers = {"User-Agent": f"AviationProject_{random_id}/1.0"}

        params = {"q": country, "format": "json", "limit": 1}

        try:

            response = get(
                url=self.openstreetmap_url, params=params, headers=headers, timeout=50
            )

            if response.status_code == 200:
                data = response.json()
                if data:
                    geo_coordinates = data[0].get("boundingbox")
                    geo_source = "Nominatim API"
        except Exception as e:
            print(f"❌ Ошибка Nominatim: {e}")

        # =============================================================
        # 2. Если сервер не дал координаты
        #    используем локальный справочник
        # =============================================================

        if not geo_coordinates:

            if country_clean in self._fallback_bounds:

                print("❌ Nominatim недоступен.")

                print("⚠️ Используем локальный справочник координат.")

                geo_coordinates = self._fallback_bounds[country_clean]

                geo_source = "Локальный справочник"

            else:

                print(f"❌ Координаты для {country} не найдены.")

                self.aeroplanes = None

                return

        # =============================================================
        # Вывод проверки координат
        # =============================================================

        print()

        print(f"✅ Источник координат: {geo_source}")

        print(f"✅ Координаты зоны: {geo_coordinates}")

        # =============================================================
        # Запрос OpenSky
        # =============================================================

        opensky_params = {
            "lamin": float(geo_coordinates[0]),  # Юг
            "lamax": float(geo_coordinates[1]),  # Север
            "lomin": float(geo_coordinates[2]),  # Запад
            "lomax": float(geo_coordinates[3]),  # Восток
        }

        print()

        print("✅ Отправляем запрос OpenSky:")

        print(opensky_params)

        try:

            response = get(url=self.opensky_url, params=opensky_params, timeout=15)

            print()

            print("✅ URL запроса:")

            print(response.url)

            if response.status_code == 200:
                self.aeroplanes = response.json()
                states = self.aeroplanes.get("states") or []  # type: ignore

                # базовая валидация данных по стране регистрации plane, чтобы не было пустых списков.
                filtered_planes = []
                for plane in states:
                    if isinstance(plane, list) and len(plane) > 2:
                        filtered_planes.append(plane)

                # Если OpenSky вернул None вместо списка возвращаем пустой список
                if self.aeroplanes is None:
                    self.aeroplanes = {"time": 0, "states": []}

                self.aeroplanes["states"] = filtered_planes
                self.offline_mode = False

                count = len(filtered_planes)
                print()
                print(f"✅ Получены реальные данные OpenSky.")
                print(f"✈️ Самолетов найдено в воздушном пространстве: {count}")
                print("    Загрузка данных ...")

            else:
                print(f"❌ OpenSky ошибка: {response.status_code}")
                # Включаем демо-режим, если сервер вернул ошибку (например, 404 или 500)
                self.offline_mode = True
                self.aeroplanes = {
                    "time": 1234567890,
                    "states": [
                        [
                            "demo1234",
                            "DEMO777 ",
                            country.strip(),
                            1234567890,
                            1234567890,
                            0.0,
                            0.0,
                            5000.0,
                            False,
                            150.0,
                            0.0,
                            0.0,
                            None,
                            5000.0,
                            None,
                            False,
                            0,
                        ]
                    ],
                }

        except Exception as e:
            print(f"❌ Ошибка OpenSky: {e}")
            print(f"❌ OpenSky недоступен.")
            print(f"⚠️ ОФФЛАЙН режим, моделирование данных авиарейсов.")
            # Включаем демо-режим, если сервер вообще не доступен (нет сети, таймаут)
            self.offline_mode = True
            self.aeroplanes = {
                "time": 1234567890,
                "states": [
                    [
                        "demo1234",
                        "DEMO777 ",
                        country.strip(),
                        1234567890,
                        1234567890,
                        0.0,
                        0.0,
                        5000.0,
                        False,
                        150.0,
                        0.0,
                        0.0,
                        None,
                        5000.0,
                        None,
                        False,
                        0,
                    ]
                ],
            }
        return self.aeroplanes


# =====================================================================
# Проверка работы модуля
# =====================================================================
if __name__ == "__main__":
    api = APIAdapter()
    country = "Canada"

    print(f"Поиск самолетов для страны: {country}")
    api.get_aeroplanes(country)

    print("\n=== Результаты обработки ответа ===")

    if api.aeroplanes and api.aeroplanes.get("states"):

        planes = api.aeroplanes["states"]

        if api.offline_mode:

            print("⚠️ ОФЛАЙН-РЕЖИМ")

            print("Примеры обнаруженных рейсов:")

        else:

            print("✅ РЕАЛЬНЫЕ ДАННЫЕ OPEN SKY")

            print("Полный список рейсов:")

        for plane in planes:
            callsign = plane[1].strip() if plane[1] else "Unknown"

            country = plane[2] if plane[2] else "Unknown"

            altitude = plane[7] if plane[7] else "На земле"

            velocity = plane[9] if plane[9] else "Нет данных"

            print(
                f"✈️ {callsign:<10}"
                f" | {country:<15}"
                f" | Высота: {altitude} м"
                f" | Скорость: {velocity} м/с"
            )

    else:

        print("❌ Самолеты не найдены.")

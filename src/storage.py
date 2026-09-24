# =====================================================================
# модуль шага 3
# =====================================================================

import json
import os
from abc import ABC, abstractmethod

# from models import Aeroplane
from src.models import Aeroplane


# =====================================================================
# 1. АБСТРАКТНЫЙ КЛАСС ДЛЯ РАБОТЫ С ХРАНИЛИЩЕМ (Шаг 3)
# =====================================================================
class BaseStorage(ABC):

    @abstractmethod
    def add_aeroplane(self, aeroplane: Aeroplane) -> None:
        """Добавить информацию о самолете в хранилище."""
        pass

    @abstractmethod
    def get_aeroplanes(
        self, min_speed: float = 0, min_altitude: float = 0
    ) -> list[dict]:
        """Получить данные из хранилища по указанным критериям."""
        pass

    @abstractmethod
    def delete_aeroplanes_by_callsign(self, callsign: str) -> None:
        """Удалить информацию о самолетах по позывному."""
        pass


# =====================================================================
# 2. РЕАЛИЗАЦИЯ JSON-КОННЕКТОРА (Шаг 3)
# =====================================================================
class JsonFileStorage(BaseStorage):

    def __init__(self, filename: str = "data/flights_data.json") -> None:
        self.filename = filename

        # Автоматически создаем папку data, если её еще нет в проекте
        dropdown_dir = os.path.dirname(self.filename)
        if dropdown_dir and not os.path.exists(dropdown_dir):
            os.makedirs(dropdown_dir)

        # Если файла нет, создаем пустой JSON-список
        if not os.path.exists(self.filename):
            self._save_to_file([])

    def _read_file(self) -> list[dict]:
        """Внутренний метод для чтения сырых данных из JSON."""
        try:
            with open(self.filename, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return []

    def _save_to_file(self, data: list[dict]) -> None:
        """Внутренний метод для записи данных в JSON."""
        with open(self.filename, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    def clear_storage(self) -> None:
        """Полностью очищает локальную базу самолетов."""
        with open(self.filename, "w", encoding="utf-8") as file:
            json.dump([], file, ensure_ascii=False, indent=4)

    # Реализация метода ДОБАВЛЕНИЯ
    def add_aeroplane(self, aeroplane: Aeroplane) -> None:
        data = self._read_file()

        # Переводим объект класса Aeroplane в словарь для записи в JSON
        plane_dict = {
            "callsign": aeroplane.callsign,
            "origin_country": aeroplane.origin_country,
            "velocity": aeroplane.velocity,
            "altitude": aeroplane.altitude,
        }

        # Предотвращаем дублирование по позывному
        data = [p for p in data if p["callsign"] != aeroplane.callsign]
        data.append(plane_dict)
        self._save_to_file(data)

    # Реализация метода ПОЛУЧЕНИЯ по критериям (Фильтрация)
    def get_aeroplanes(
        self, min_speed: float = 0, min_altitude: float = 0
    ) -> list[dict]:
        all_planes = self._read_file()
        filtered_planes = []

        for p in all_planes:
            if p["velocity"] >= min_speed and p["altitude"] >= min_altitude:
                filtered_planes.append(p)

        return filtered_planes

    # Реализация метода УДАЛЕНИЯ
    def delete_aeroplanes_by_callsign(self, callsign: str) -> None:
        data = self._read_file()
        clean_callsign = callsign.strip().upper()

        # Оставляем только те самолеты, чей позывной не совпадает с удаляемым
        filtered_data = [
            p for p in data if p["callsign"].strip().upper() != clean_callsign
        ]

        if len(data) != len(filtered_data):
            print(f"🗑️ Из файла удален самолет с позывным {clean_callsign}.")
        else:
            print(f"❌ Самолет с позывным {clean_callsign} не найден в файле.")

        self._save_to_file(filtered_data)

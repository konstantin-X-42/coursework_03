import psycopg2
from psycopg2.extras import RealDictCursor


class DBManager:
    """Класс для подключения к БД PostgreSQL и выполнения аналитических запросов."""

    def __init__(self, db_params: dict) -> None:
        """
        Инициализация менеджера базы данных.
        :param db_params: Словарь с параметрами подключения (host, user, password, port, database).
        """
        self.db_params = db_params
        self.create_tables()

    def _execute_query(self, query: str, params: tuple = None, fetch: bool = False) -> list:
        """Вспомогательный метод для безопасного открытия соединения и выполнения запросов."""
        conn = psycopg2.connect(**self.db_params)
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(query, params or ())
                if fetch:
                    return cur.fetchall()
                conn.commit()
        finally:
            conn.close()

    def create_tables(self) -> None:
        """Создает таблицы стран и самолетов, если они отсутствуют."""
        query = """
        CREATE TABLE IF NOT EXISTS countries (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) UNIQUE NOT NULL
        );

        CREATE TABLE IF NOT EXISTS aeroplanes (
            id SERIAL PRIMARY KEY,
            callsign VARCHAR(20) NOT NULL,
            velocity NUMERIC DEFAULT 0.0,
            altitude NUMERIC DEFAULT 0.0,
            country_id INTEGER REFERENCES countries(id) ON DELETE CASCADE
        );
        """
        self._execute_query(query)

    def clear_tables(self) -> None:
        """Очищает таблицы перед новой сессией загрузки данных из API."""
        query = "TRUNCATE TABLE countries CASCADE;"
        self._execute_query(query)

    def save_aeroplanes_data(self, country_name: str, planes_list: list) -> None:
        """
        Сохраняет страну и список объектов самолетов Aeroplane в базу данных.
        """
        conn = psycopg2.connect(**self.db_params)
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO countries (name) VALUES (%s) 
                    ON CONFLICT (name) DO UPDATE SET name=EXCLUDED.name 
                    RETURNING id;
                    """,
                    (country_name,)
                )
                country_id = cur.fetchone()[0]

                for plane in planes_list:
                    cur.execute(
                        """
                        INSERT INTO aeroplanes (callsign, velocity, altitude, country_id)
                        VALUES (%s, %s, %s, %s);
                        """,
                        (plane.callsign, plane.velocity, plane.altitude, country_id)
                    )
            conn.commit()
        finally:
            conn.close()

    # =====================================================================
    # МЕТОДЫ ИЗ ТЕХНИЧЕСКОГО ЗАДАНИЯ
    # =====================================================================

    def get_countries_and_aeroplanes_count(self) -> list[dict]:
        """Получает список всех стран и количество самолетов в их воздушных пространствах."""
        query = """
        SELECT c.name AS country, COUNT(a.id) AS aeroplanes_count
        FROM countries c
        LEFT JOIN aeroplanes a ON c.id = a.country_id
        GROUP BY c.id, c.name
        ORDER BY aeroplanes_count DESC;
        """
        return self._execute_query(query, fetch=True)

    def get_all_aeroplanes(self) -> list[dict]:
        """Получает список всех воздушных судов."""
        query = """
        SELECT a.callsign, c.name AS origin_country, a.velocity, a.altitude
        FROM aeroplanes a
        JOIN countries c ON a.country_id = c.id
        ORDER BY a.callsign;
        """
        return self._execute_query(query, fetch=True)

    def get_avg_speed(self) -> float:
        """Получает среднюю скорость по самолетам."""
        query = "SELECT AVG(velocity) AS avg_speed FROM aeroplanes;"
        result = self._execute_query(query, fetch=True)
        if result and result[0]['avg_speed'] is not None:
            return float(result[0]['avg_speed'])
        return 0.0

    def get_aeroplanes_with_higher_speed(self) -> list[dict]:
        """Получает список всех самолетов, у которых скорость выше средней."""
        query = """
        SELECT a.callsign, c.name AS origin_country, a.velocity, a.altitude
        FROM aeroplanes a
        JOIN countries c ON a.country_id = c.id
        WHERE a.velocity > (SELECT COALESCE(AVG(velocity), 0) FROM aeroplanes)
        ORDER BY a.velocity DESC;
        """
        return self._execute_query(query, fetch=True)

    def get_aeroplanes_with_keyword(self, keyword: str) -> list[dict]:
        """Получает список всех самолетов, в позывном которых содержатся переданные символы."""
        query = """
        SELECT a.callsign, c.name AS origin_country, a.velocity, a.altitude
        FROM aeroplanes a
        JOIN countries c ON a.country_id = c.id
        WHERE a.callsign ILIKE %s
        ORDER BY a.callsign;
        """
        return self._execute_query(query, (f"%{keyword.strip()}%",), fetch=True)






# # =====================================================================
# # модуль шага 3
# # =====================================================================
#
# import json
# import os
# from abc import ABC, abstractmethod
#
# # from models import Aeroplane
# from src.models import Aeroplane
#
#
# # =====================================================================
# # 1. АБСТРАКТНЫЙ КЛАСС ДЛЯ РАБОТЫ С ХРАНИЛИЩЕМ (Шаг 3)
# # =====================================================================
# class BaseStorage(ABC):
#
#     @abstractmethod
#     def add_aeroplane(self, aeroplane: Aeroplane) -> None:
#         """Добавить информацию о самолете в хранилище."""
#         pass
#
#     @abstractmethod
#     def get_aeroplanes(
#         self, min_speed: float = 0, min_altitude: float = 0
#     ) -> list[dict]:
#         """Получить данные из хранилища по указанным критериям."""
#         pass
#
#     @abstractmethod
#     def delete_aeroplanes_by_callsign(self, callsign: str) -> None:
#         """Удалить информацию о самолетах по позывному."""
#         pass
#
#
# # =====================================================================
# # 2. РЕАЛИЗАЦИЯ JSON-КОННЕКТОРА (Шаг 3)
# # =====================================================================
# class JsonFileStorage(BaseStorage):
#
#     def __init__(self, filename: str = "data/flights_data.json") -> None:
#         self.filename = filename
#
#         # Автоматически создаем папку data, если её еще нет в проекте
#         dropdown_dir = os.path.dirname(self.filename)
#         if dropdown_dir and not os.path.exists(dropdown_dir):
#             os.makedirs(dropdown_dir)
#
#         # Если файла нет, создаем пустой JSON-список
#         if not os.path.exists(self.filename):
#             self._save_to_file([])
#
#     def _read_file(self) -> list[dict]:
#         """Внутренний метод для чтения сырых данных из JSON."""
#         try:
#             with open(self.filename, "r", encoding="utf-8") as f:
#                 return json.load(f)
#         except (json.JSONDecodeError, IOError):
#             return []
#
#     def _save_to_file(self, data: list[dict]) -> None:
#         """Внутренний метод для записи данных в JSON."""
#         with open(self.filename, "w", encoding="utf-8") as f:
#             json.dump(data, f, ensure_ascii=False, indent=4)
#
#     def clear_storage(self) -> None:
#         """Полностью очищает локальную базу самолетов."""
#         with open(self.filename, "w", encoding="utf-8") as file:
#             json.dump([], file, ensure_ascii=False, indent=4)
#
#     # Реализация метода ДОБАВЛЕНИЯ
#     def add_aeroplane(self, aeroplane: Aeroplane) -> None:
#         data = self._read_file()
#
#         # Переводим объект класса Aeroplane в словарь для записи в JSON
#         plane_dict = {
#             "callsign": aeroplane.callsign,
#             "origin_country": aeroplane.origin_country,
#             "velocity": aeroplane.velocity,
#             "altitude": aeroplane.altitude,
#         }
#
#         # Предотвращаем дублирование по позывному
#         data = [p for p in data if p["callsign"] != aeroplane.callsign]
#         data.append(plane_dict)
#         self._save_to_file(data)
#
#     # Реализация метода ПОЛУЧЕНИЯ по критериям (Фильтрация)
#     def get_aeroplanes(
#         self, min_speed: float = 0, min_altitude: float = 0
#     ) -> list[dict]:
#         all_planes = self._read_file()
#         filtered_planes = []
#
#         for p in all_planes:
#             if p["velocity"] >= min_speed and p["altitude"] >= min_altitude:
#                 filtered_planes.append(p)
#
#         return filtered_planes
#
#     # Реализация метода УДАЛЕНИЯ
#     def delete_aeroplanes_by_callsign(self, callsign: str) -> None:
#         data = self._read_file()
#         clean_callsign = callsign.strip().upper()
#
#         # Оставляем только те самолеты, чей позывной не совпадает с удаляемым
#         filtered_data = [
#             p for p in data if p["callsign"].strip().upper() != clean_callsign
#         ]
#
#         if len(data) != len(filtered_data):
#             print(f"🗑️ Из файла удален самолет с позывным {clean_callsign}.")
#         else:
#             print(f"❌ Самолет с позывным {clean_callsign} не найден в файле.")
#
#         self._save_to_file(filtered_data)

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

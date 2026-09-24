from unittest.mock import MagicMock, patch
import pytest
from src.db_manager import DBManager
from src.models import Aeroplane


@pytest.fixture
def mock_db_params():
    """Фикстура с фейковыми параметрами подключения для тестов."""
    return {
        "host": "localhost",
        "port": 5432,
        "user": "test_user",
        "password": "test_password",
        "database": "test_db"
    }


@patch("src.db_manager.psycopg2.connect")
def test_db_manager_initialization_creates_tables(mock_connect, mock_db_params):
    """Проверяет, что при создании DBManager автоматически создаются таблицы."""
    DBManager(db_params=mock_db_params)

    # Проверяем, что соединение было открыто
    mock_connect.assert_called_once_with(**mock_db_params)
    # Проверяем, что курсор был создан и метод execute вызвался для создания таблиц
    mock_conn_obj = mock_connect.return_value
    mock_cursor = mock_conn_obj.cursor.return_value.__enter__.return_value
    assert mock_cursor.execute.called


@patch("src.db_manager.DBManager._execute_query")
def test_get_countries_and_aeroplanes_count(mock_execute, mock_db_params):
    """Проверяет корректность метода подсчета самолетов по странам (Метод 1 из ТЗ)."""
    mock_data = [
        {"country": "Canada", "aeroplanes_count": 15},
        {"country": "USA", "aeroplanes_count": 42}
    ]
    mock_execute.return_value = mock_data

    db = DBManager(db_params=mock_db_params)
    result = db.get_countries_and_aeroplanes_count()

    assert result == mock_data
    assert len(result) == 2
    assert result[0]["country"] == "Canada"


@patch("src.db_manager.DBManager._execute_query")
def test_get_all_aeroplanes(mock_execute, mock_db_params):
    """Проверяет получение полного списка всех воздушных судов."""
    mock_data = [
        {"callsign": "ACA123", "origin_country": "Canada", "velocity": 250.0, "altitude": 10000.0}
    ]
    mock_execute.return_value = mock_data

    db = DBManager(db_params=mock_db_params)
    result = db.get_all_aeroplanes()

    assert result == mock_data
    assert result[0]["callsign"] == "ACA123"


@patch("src.db_manager.DBManager._execute_query")
def test_get_avg_speed(mock_execute, mock_db_params):
    """Проверяет расчет средней скорости."""
    # Тест случая, когда в базе есть данные
    mock_execute.return_value = [{"avg_speed": 210.5}]
    db = DBManager(db_params=mock_db_params)
    assert db.get_avg_speed() == 210.5

    # Тест случая, когда база пуста и AVG() возвращает None
    mock_execute.return_value = [{"avg_speed": None}]
    assert db.get_avg_speed() == 0.0


@patch("src.db_manager.DBManager._execute_query")
def test_get_aeroplanes_with_higher_speed(mock_execute, mock_db_params):
    """Проверяет фильтрацию самолетов со скоростью выше средней."""
    mock_data = [
        {"callsign": "FAST99", "origin_country": "USA", "velocity": 350.0, "altitude": 11000.0}
    ]
    mock_execute.return_value = mock_data

    db = DBManager(db_params=mock_db_params)
    result = db.get_aeroplanes_with_higher_speed()

    assert len(result) == 1
    assert result[0]["callsign"] == "FAST99"


@patch("src.db_manager.DBManager._execute_query")
def test_get_aeroplanes_with_keyword(mock_execute, mock_db_params):
    """Проверяет регистронезависимый поиск по ключевому слову в позывном."""
    mock_data = [
        {"callsign": "ACA123", "origin_country": "Canada", "velocity": 200.0, "altitude": 9000.0}
    ]
    mock_execute.return_value = mock_data

    db = DBManager(db_params=mock_db_params)
    result = db.get_aeroplanes_with_keyword("ACA")

    assert len(result) == 1
    # Проверяем, что в метод _execute_query прокинулся кортеж с процентами для SQL-оператора LIKE
    mock_execute.assert_called_with(
        """
        SELECT a.callsign, c.name AS origin_country, a.velocity, a.altitude
        FROM aeroplanes a
        JOIN countries c ON a.country_id = c.id
        WHERE a.callsign ILIKE %s
        ORDER BY a.callsign;
        """,
        ("%ACA%",),
        fetch=True
    )

# import json
#
# import pytest
#
# from src.models import Aeroplane
# from src.db_manager import BaseStorage, JsonFileStorage
#
# # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# # запуск тестов в модуле test_db_manager.py с покрытием в html
# # poetry run pytest tests/test_db_manager.py --cov=storage --cov-report=html
# # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#
# # =====================================================================
# # Проверка абстрактного класса
# # =====================================================================
#
# def test_base_storage_is_abstract():
#     """
#     BaseStorage нельзя создать напрямую,
#     так как он содержит абстрактные методы.
#     """
#
#     with pytest.raises(TypeError):
#         BaseStorage()
#
#
# # =====================================================================
# # Фикстура временного JSON-хранилища
# # =====================================================================
#
# @pytest.fixture
# def storage(tmp_path):
#     """
#     Создает временный JSON-файл
#     для каждого теста.
#     """
#
#     file_path = tmp_path / "flights.json"
#
#     return JsonFileStorage(filename=str(file_path))
#
#
# # =====================================================================
# # Проверка создания файла
# # =====================================================================
#
# def test_storage_creates_file(tmp_path):
#     """
#     При создании JsonFileStorage
#     файл должен появиться автоматически.
#     """
#
#     file_path = tmp_path / "data.json"
#
#     JsonFileStorage(filename=str(file_path))
#
#     assert file_path.exists()
#
#     with open(file_path, encoding="utf-8") as f:
#         data = json.load(f)
#
#     assert data == []
#
#
# # =====================================================================
# # Добавление самолета
# # =====================================================================
#
# def test_add_aeroplane(storage):
#     """
#     Самолет добавляется в JSON.
#     """
#
#     plane = Aeroplane("AFL123", "Russia", 250.0, 10000.0)
#
#     storage.add_aeroplane(plane)
#
#     result = storage.get_aeroplanes()
#
#     assert len(result) == 1
#     assert result[0]["callsign"] == "AFL123"
#     assert result[0]["origin_country"] == "Russia"
#     assert result[0]["velocity"] == 250.0
#     assert result[0]["altitude"] == 10000.0
#
#
# # =====================================================================
# # Проверка отсутствия дублей
# # =====================================================================
#
# def test_add_same_callsign_updates_plane(storage):
#     """При повторном добавлении самолета с тем же callsign старый заменяется."""
#
#     plane1 = Aeroplane("TEST001", "USA", 100, 3000)
#
#     plane2 = Aeroplane("TEST001", "USA", 300, 9000)
#
#     storage.add_aeroplane(plane1)
#     storage.add_aeroplane(plane2)
#
#     result = storage.get_aeroplanes()
#
#     assert len(result) == 1
#     assert result[0]["velocity"] == 300
#     assert result[0]["altitude"] == 9000
#
#
# # =====================================================================
# # Фильтрация
# # =====================================================================
#
# def test_filter_by_speed(storage):
#
#     storage.add_aeroplane(Aeroplane("FAST", "USA", 500, 5000))
#
#     storage.add_aeroplane(Aeroplane("SLOW", "USA", 100, 5000))
#
#     result = storage.get_aeroplanes(min_speed=300)
#
#     assert len(result) == 1
#     assert result[0]["callsign"] == "FAST"
#
#
# def test_filter_by_altitude(storage):
#
#     storage.add_aeroplane(Aeroplane("HIGH", "USA", 300, 12000))
#
#     storage.add_aeroplane(Aeroplane("LOW", "USA", 300, 2000))
#
#     result = storage.get_aeroplanes(min_altitude=5000)
#
#     assert len(result) == 1
#     assert result[0]["callsign"] == "HIGH"
#
#
# def test_filter_by_speed_and_altitude(storage):
#
#     storage.add_aeroplane(Aeroplane("OK", "USA", 300, 10000))
#
#     result = storage.get_aeroplanes(min_speed=200, min_altitude=5000)
#
#     assert len(result) == 1
#
#
# # =====================================================================
# # Удаление
# # =====================================================================
#
# def test_delete_aeroplane(storage):
#
#     storage.add_aeroplane(Aeroplane("DEL001", "Germany", 200, 4000))
#
#     storage.delete_aeroplanes_by_callsign("DEL001")
#
#     result = storage.get_aeroplanes()
#
#     assert result == []
#
#
# def test_delete_case_insensitive(storage):
#
#     storage.add_aeroplane(Aeroplane("ABC123", "France", 200, 5000))
#
#     storage.delete_aeroplanes_by_callsign(" abc123 ")
#
#     assert storage.get_aeroplanes() == []
#
#
# def test_delete_not_existing(storage):
#
#     storage.add_aeroplane(Aeroplane("AAA", "USA", 100, 1000))
#
#     # Ошибки быть не должно
#     storage.delete_aeroplanes_by_callsign("BBB")
#
#     assert len(storage.get_aeroplanes()) == 1
#
#
# # =====================================================================
# # Проверка поврежденного JSON
# # =====================================================================
#
# def test_broken_json_returns_empty(tmp_path):
#
#     file_path = tmp_path / "broken.json"
#
#     with open(file_path, "w") as f:
#         f.write("broken json")
#
#     storage = JsonFileStorage(filename=str(file_path))
#
#     assert storage.get_aeroplanes() == []

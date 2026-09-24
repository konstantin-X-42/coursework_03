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
    """Проверяет корректность метода подсчета самолетов по странам."""
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
    """Проверяет регистронезависимый поиск по ключевому слову в позывном"""
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

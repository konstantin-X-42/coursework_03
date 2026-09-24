from unittest.mock import MagicMock, patch

import pytest

from src.api import APIAdapter, BaseAPIAdapter

# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# запуск тестов в модуле test_api.py с покрытием в html
# poetry run pytest tests/test_api.py --cov=api --cov-report=html
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

# =====================================================================
# Проверка абстрактного класса
# =====================================================================


def test_base_api_adapter_is_abstract():
    """
    BaseAPIAdapter нельзя создать напрямую.
    """

    with pytest.raises(TypeError):
        BaseAPIAdapter()


# =====================================================================
# Проверка создания APIAdapter
# =====================================================================


def test_api_adapter_creation():
    """
    Проверяем начальное состояние объекта.
    """

    api = APIAdapter()

    assert api.aeroplanes is None
    assert "canada" in api._fallback_bounds
    assert "russia" in api._fallback_bounds


# =====================================================================
# Проверка успешного получения координат через OpenStreetMap
# =====================================================================


@patch("src.api.get")
def test_get_aeroplanes_success(mock_get):
    """
    Проверяем успешный сценарий:
    1. OpenStreetMap возвращает координаты.
    2. OpenSky возвращает самолеты.
    """

    # Первый вызов - OpenStreetMap
    osm_response = MagicMock()
    osm_response.status_code = 200
    osm_response.json.return_value = [
        {"boundingbox": ["41.67", "83.11", "-141.00", "-52.62"]}
    ]

    # Второй вызов - OpenSky
    opensky_response = MagicMock()
    opensky_response.status_code = 200
    opensky_response.json.return_value = {
        "time": 123456,
        "states": [["abc123", "TEST001", "Canada"]],
    }

    mock_get.side_effect = [osm_response, opensky_response]

    api = APIAdapter()

    api.get_aeroplanes("Canada")

    assert api.aeroplanes is not None
    assert "states" in api.aeroplanes
    assert len(api.aeroplanes["states"]) == 1


# =====================================================================
# Проверка fallback координат
# =====================================================================


@patch("src.api.get")
def test_get_aeroplanes_fallback(mock_get):
    """
    Если OpenStreetMap недоступен,
    используются локальные координаты.
    """

    # Ошибка первого запроса
    mock_get.side_effect = Exception("Connection error")

    api = APIAdapter()

    # После ошибки OpenSky тоже не вызывается,
    # поэтому самолетов не будет
    api.get_aeroplanes("Canada")

    assert api.offline_mode is True
    assert api.aeroplanes is not None
    assert "demo1234" in api.aeroplanes["states"][0]


# =====================================================================
# Проверка неизвестной страны
# =====================================================================


@patch("src.api.get")
def test_unknown_country(mock_get):
    """
    Страна отсутствует в локальном справочнике.
    """

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = []

    mock_get.return_value = mock_response

    api = APIAdapter()

    api.get_aeroplanes("Atlantis")

    assert api.aeroplanes is None


# =====================================================================
# Проверка ошибки OpenSky
# =====================================================================


@patch("src.api.get")
def test_opensky_error_generates_demo_data(mock_get):
    """
    Если OpenSky отвечает ошибкой,
    должен включиться демонстрационный режим.
    """

    osm_response = MagicMock()
    osm_response.status_code = 200
    osm_response.json.return_value = [
        {"boundingbox": ["41.67", "83.11", "-141.00", "-52.62"]}
    ]

    opensky_response = MagicMock()
    opensky_response.status_code = 500

    mock_get.side_effect = [osm_response, opensky_response]

    api = APIAdapter()

    api.get_aeroplanes("Canada")

    assert api.aeroplanes is not None
    assert "states" in api.aeroplanes
    assert len(api.aeroplanes["states"]) == 1


# =====================================================================
# Проверка ошибки JSON OpenSky
# =====================================================================


@patch("src.api.get")
def test_opensky_connection_exception(mock_get):
    """
    Ошибка соединения с OpenSky.
    """

    osm_response = MagicMock()
    osm_response.status_code = 200
    osm_response.json.return_value = [
        {"boundingbox": ["41.67", "83.11", "-141.00", "-52.62"]}
    ]

    mock_get.side_effect = [osm_response, Exception("Server unavailable")]

    api = APIAdapter()

    api.get_aeroplanes("Canada")

    assert api.offline_mode is True
    assert api.aeroplanes is not None
    assert "demo1234" in api.aeroplanes["states"][0]

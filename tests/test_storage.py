import json

import pytest

from src.models import Aeroplane
from src.storage import BaseStorage, JsonFileStorage

# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# запуск тестов в модуле test_storage.py с покрытием в html
# poetry run pytest tests/test_storage.py --cov=storage --cov-report=html
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

# =====================================================================
# Проверка абстрактного класса
# =====================================================================

def test_base_storage_is_abstract():
    """
    BaseStorage нельзя создать напрямую,
    так как он содержит абстрактные методы.
    """

    with pytest.raises(TypeError):
        BaseStorage()


# =====================================================================
# Фикстура временного JSON-хранилища
# =====================================================================

@pytest.fixture
def storage(tmp_path):
    """
    Создает временный JSON-файл
    для каждого теста.
    """

    file_path = tmp_path / "flights.json"

    return JsonFileStorage(filename=str(file_path))


# =====================================================================
# Проверка создания файла
# =====================================================================

def test_storage_creates_file(tmp_path):
    """
    При создании JsonFileStorage
    файл должен появиться автоматически.
    """

    file_path = tmp_path / "data.json"

    JsonFileStorage(filename=str(file_path))

    assert file_path.exists()

    with open(file_path, encoding="utf-8") as f:
        data = json.load(f)

    assert data == []


# =====================================================================
# Добавление самолета
# =====================================================================

def test_add_aeroplane(storage):
    """
    Самолет добавляется в JSON.
    """

    plane = Aeroplane("AFL123", "Russia", 250.0, 10000.0)

    storage.add_aeroplane(plane)

    result = storage.get_aeroplanes()

    assert len(result) == 1
    assert result[0]["callsign"] == "AFL123"
    assert result[0]["origin_country"] == "Russia"
    assert result[0]["velocity"] == 250.0
    assert result[0]["altitude"] == 10000.0


# =====================================================================
# Проверка отсутствия дублей
# =====================================================================

def test_add_same_callsign_updates_plane(storage):
    """При повторном добавлении самолета с тем же callsign старый заменяется."""

    plane1 = Aeroplane("TEST001", "USA", 100, 3000)

    plane2 = Aeroplane("TEST001", "USA", 300, 9000)

    storage.add_aeroplane(plane1)
    storage.add_aeroplane(plane2)

    result = storage.get_aeroplanes()

    assert len(result) == 1
    assert result[0]["velocity"] == 300
    assert result[0]["altitude"] == 9000


# =====================================================================
# Фильтрация
# =====================================================================

def test_filter_by_speed(storage):

    storage.add_aeroplane(Aeroplane("FAST", "USA", 500, 5000))

    storage.add_aeroplane(Aeroplane("SLOW", "USA", 100, 5000))

    result = storage.get_aeroplanes(min_speed=300)

    assert len(result) == 1
    assert result[0]["callsign"] == "FAST"


def test_filter_by_altitude(storage):

    storage.add_aeroplane(Aeroplane("HIGH", "USA", 300, 12000))

    storage.add_aeroplane(Aeroplane("LOW", "USA", 300, 2000))

    result = storage.get_aeroplanes(min_altitude=5000)

    assert len(result) == 1
    assert result[0]["callsign"] == "HIGH"


def test_filter_by_speed_and_altitude(storage):

    storage.add_aeroplane(Aeroplane("OK", "USA", 300, 10000))

    result = storage.get_aeroplanes(min_speed=200, min_altitude=5000)

    assert len(result) == 1


# =====================================================================
# Удаление
# =====================================================================

def test_delete_aeroplane(storage):

    storage.add_aeroplane(Aeroplane("DEL001", "Germany", 200, 4000))

    storage.delete_aeroplanes_by_callsign("DEL001")

    result = storage.get_aeroplanes()

    assert result == []


def test_delete_case_insensitive(storage):

    storage.add_aeroplane(Aeroplane("ABC123", "France", 200, 5000))

    storage.delete_aeroplanes_by_callsign(" abc123 ")

    assert storage.get_aeroplanes() == []


def test_delete_not_existing(storage):

    storage.add_aeroplane(Aeroplane("AAA", "USA", 100, 1000))

    # Ошибки быть не должно
    storage.delete_aeroplanes_by_callsign("BBB")

    assert len(storage.get_aeroplanes()) == 1


# =====================================================================
# Проверка поврежденного JSON
# =====================================================================

def test_broken_json_returns_empty(tmp_path):

    file_path = tmp_path / "broken.json"

    with open(file_path, "w") as f:
        f.write("broken json")

    storage = JsonFileStorage(filename=str(file_path))

    assert storage.get_aeroplanes() == []

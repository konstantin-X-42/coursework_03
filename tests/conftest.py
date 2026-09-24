import os
import shutil

import pytest

from src.storage import JsonFileStorage

# =====================================================================
# Фикстура временного JSON-хранилища
# Используется в:
# - test_storage.py
# - test_main.py
# =====================================================================


@pytest.fixture
def temp_storage():
    """
    Создает временное хранилище JSON для тестов.
    После завершения теста удаляет созданную папку.
    """

    test_dir = "data_test"
    test_file = f"{test_dir}/test_flights.json"

    storage = JsonFileStorage(filename=test_file)

    yield storage

    if os.path.exists(test_dir):
        shutil.rmtree(test_dir)


# =====================================================================
# Тестовые данные ответа OpenSky API
# Используется в:
# - test_api.py
# - test_main.py
# =====================================================================


@pytest.fixture
def fake_api_data():
    """
    Имитация ответа OpenSky API.
    """

    return {
        "time": 1700000000,
        "states": [
            [
                "c820b3",
                "AAA111",
                "Canada",
                1700000100,
                1700000100,
                -75.67,
                45.42,
                10000.0,
                False,
                250.5,
            ],
            [
                "a143b8",
                "BBB222",
                "USA",
                1700000100,
                1700000100,
                -114.07,
                51.04,
                5000.0,
                False,
                150.2,
            ],
        ],
    }

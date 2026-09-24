import pytest

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

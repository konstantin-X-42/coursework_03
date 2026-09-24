import pytest

from src.models import Aeroplane

# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# запуск тестов в модуле test_models.py с покрытием в html
# poetry run pytest tests/test_models.py --cov=models --cov-report=html
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

# =====================================================================
# Тесты конструктора
# =====================================================================

def test_create_aeroplane():
    """Корректное создание объекта."""
    plane = Aeroplane(
        callsign="  AFL123  ",
        origin_country="Russia",
        velocity=250.5,
        altitude=10000.0,
    )

    assert plane.callsign == "AFL123"
    assert plane.origin_country == "Russia"
    assert plane.velocity == 250.5
    assert plane.altitude == 10000.0


def test_none_values():
    """None должны заменяться значениями по умолчанию."""
    plane = Aeroplane(
        callsign=None,
        origin_country=None,
        velocity=None,
        altitude=None,
    )

    assert plane.callsign == "UNKNOWN"
    assert plane.origin_country == "Unknown"
    assert plane.velocity == 0.0
    assert plane.altitude == 0.0


# =====================================================================
# Тест метода __repr__
# =====================================================================

def test_repr():
    """Проверка текстового представления объекта."""
    plane = Aeroplane(
        "TEST100",
        "France",
        200.0,
        5000.0,
    )

    expected = (
        "Aeroplane(Callsign: TEST100, "
        "Country: France, "
        "Speed: 200.0 m/s, "
        "Alt: 5000.0 m)"
    )

    assert repr(plane) == expected


# =====================================================================
# Тесты сравнения
# =====================================================================

def test_speed_comparison():
    """Сравнение по скорости."""
    slow = Aeroplane("A", "USA", 150.0, 3000.0)
    fast = Aeroplane("B", "USA", 250.0, 3000.0)

    assert slow < fast
    assert fast > slow
    assert not fast < slow
    assert not slow > fast


def test_speed_equality():
    """Самолеты с одинаковой скоростью считаются равными."""
    plane1 = Aeroplane("A", "USA", 250.0, 1000.0)
    plane2 = Aeroplane("B", "Germany", 250.0, 9000.0)

    assert plane1 == plane2


def test_height_comparison():
    """Сравнение по высоте."""
    high = Aeroplane("HIGH", "USA", 200.0, 10000.0)
    low = Aeroplane("LOW", "USA", 300.0, 5000.0)

    assert high.is_higher_than(low)
    assert not low.is_higher_than(high)


# =====================================================================
# Проверка сравнения с объектом другого типа
# =====================================================================

def test_compare_with_other_type():
    """При сравнении с другим типом должен возникнуть TypeError."""
    plane = Aeroplane("AAA", "USA", 200.0, 5000.0)

    with pytest.raises(TypeError):
        plane < 10

    with pytest.raises(TypeError):
        plane > "text"

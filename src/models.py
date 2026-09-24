# =====================================================================
# модуль шага 2
# =====================================================================

class Aeroplane:

    def __init__(
        self, callsign: str, origin_country: str, velocity: float, altitude: float
    ) -> None:
        # Валидация входных данных
        self.callsign = str(callsign).strip() if callsign else "UNKNOWN"
        self.origin_country = str(origin_country) if origin_country else "Unknown"

        # Если самолет на земле, скорость и высота могут быть None. Превращаем в 0.0
        self.velocity = float(velocity) if velocity is not None else 0.0
        self.altitude = float(altitude) if altitude is not None else 0.0

    def __repr__(self) -> str:
        """Текстовое представление объекта в коде."""
        return f"Aeroplane(Callsign: {self.callsign}, Country: {self.origin_country}, Speed: {self.velocity} m/s, Alt: {self.altitude} m)"

    # =====================================================================
    # МЕТОДЫ СРАВНЕНИЯ (Магические методы dunder)
    # =====================================================================

    # 1. Сравнение ПО ВЫСОТЕ (Меньше / Больше / Равно)
    def is_higher_than(self, other: "Aeroplane") -> bool:
        """Метод для явного сравнения высоты."""
        return self.altitude > other.altitude

    # 2. Сравнение ПО СКОРОСТИ через стандартные операторы Python (<, >, ==)
    def __lt__(self, other: "Aeroplane") -> bool:
        """Оператор 'меньше' (<) — сравнивает самолеты по скорости."""
        if not isinstance(other, Aeroplane):
            return NotImplemented
        return self.velocity < other.velocity

    def __gt__(self, other: "Aeroplane") -> bool:
        """Оператор 'больше' (>) — сравнивает самолеты по скорости."""
        if not isinstance(other, Aeroplane):
            return NotImplemented
        return self.velocity > other.velocity

    # def __eq__(self, other: "Aeroplane") -> bool:
    #     """Оператор 'равно' (==) — проверяет равенство скоростей."""
    #     if not isinstance(other, Aeroplane):
    #         return NotImplemented
    #     return self.velocity == other.velocity

    def __eq__(self, other: object) -> bool:
        """Оператор 'равно' (==) — проверяет равенство скоростей."""
        if not isinstance(other, Aeroplane):
            return NotImplemented
        return self.velocity == other.velocity

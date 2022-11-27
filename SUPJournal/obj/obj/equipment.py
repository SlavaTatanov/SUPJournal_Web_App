class Equipment:
    """Базовый класс для снаряжения"""
    def __init__(self, name):
        self.name = name
        self.km = 0


class SupBoard(Equipment):
    """Снаряжение - САП доска"""
    def __init__(self, name, width, length):
        super().__init__(name)
        self.width = width
        self.length = length


class Paddle(Equipment):
    """Снаряжение - весло"""
    def __init__(self, name):
        super().__init__(name)

import arcade
from typing import List, Dict, Union, Optional
# from buildings import Building
from resources import *
from constants import Building

# ----------- ЯДРО (немного изменённое) -----------
class Core(Building):
    """Ядро - бесконечное хранилище"""

    def __init__(self, scale: float, x: float, y: float):
        # У ядра бесконечное хранилище
        cost = ResourceTransaction()  # Бесплатное

        super().__init__(
            image_path="Изображения/Здания/Ядро (2).png",
            scale=scale,
            x=x, y=y,
            name="Ядро",
            hp=20,  # У ядра больше HP
            cost=cost,
            storage_capacity=None
        )

        # Начальные ресурсы
        self.storage.add("Медь", 10)
        self.storage.add("Олово", 5)
        self.storage.add("Уголь", 5)

    # Ядро не производит ничего
    def _produce(self):
        pass


x = Core(0.25, 1, 1)
print(x)
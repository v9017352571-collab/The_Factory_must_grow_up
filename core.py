import arcade
from typing import List, Dict, Union, Optional
from buildings import Building
from resources import *
from random import randint

# ----------- ЯДРО (немного изменённое) -----------
class Core(Building):
    """Ядро - бесконечное хранилище"""

    def __init__(self, scale: float, x: float, y: float):
        super().__init__(
            image_path="Изображения/Здания/Ядро (2).png",
            scale=scale,
            x=x, y=y,
            name="Ядро",
            capacity=None  # None = бесконечное хранилище
        )

        # Начальные ресурсы
        self.storage.add("Медь", 10)
        self.storage.add("Олово", 5)
        self.storage.add("Уголь", 5)

        self.production_time = 1.0

    # Ядро не производит ничего
    def _produce(self):
        """производит уголь, медь, олово и кремний(последний с шансом в 10%)"""
        self.add('уголь')
        self.add('медь')
        self.add('олово')
        if randint(1, 10) == 1:
            self.add('кремний')
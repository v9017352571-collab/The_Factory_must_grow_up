# core.py
import arcade
from typing import List, Dict, Union, Optional


class ResourceCost(dict):
    """Основной класс для оптимизации эконом. системы"""

    def __init__(self, capacity: dict | bool,
                 cost: dict | None = None,
                 input_resource: str | None = None, output_resource: str | None = None,
                 is_core: bool = False):
        """
        Инициализация хранилища здания.

        capacity: dict | bool - тип хранимого ресурса и максимальное количество или True если неограниченное кол-во.
        input_resource и output_resource : str | None - входные и выходные ресурсы
        is_core: bool - True только если это хранилище ядра
        cost: dict | None - стоимость здания. None - стандартная цена

        self.capacity: dict | bool - тип хранимого ресурса и максимальное количество или True если неограниченное кол-во
        self.input_resource: str | None
        self.output_resource: str | None
        self.is_core: bool
        self.cost: dict - стоимость здания. Стандартная цена 1 медь
        """
        if is_core:
            super().__init__({
            "Медь": 10,
            "Олово": 5,
            "Уголь": 5,
            "Бронза": 0,
            "Кремний": 0,
            "Микросхема": 0,
            "Боеприпасы": 0
        })
        elif capacity is True:
            super().__init__({
                "Медь": 0,
                "Олово": 0,
                "Уголь": 0,
                "Бронза": 0,
                "Кремний": 0,
                "Микросхема": 0,
                "Боеприпасы": 0
            })
        else:
            super().__init__()
            for key in capacity.keys():
                self[key] = 0

        self.cost = {'Медь', 1} if cost is None else cost
        self.input_resource = input_resource
        self.output_resource = output_resource
        self.capacity = capacity

    def has_resources(self, di: dict) -> bool:
        """проверяет наличие нужного количества ресурсов
        True если хватает, False если нет"""
        return all(self.get(key, 0) <= val for key, val in di.items())

    def deduct_resources(self, di: dict):
        """вычитает ресурсы из хранилища"""
        for key, val in di.items():
            self[key] -= val

    def try_spend_resources(self, di: dict):
        """тратит ресурсы если они есть в хранилище"""
        if self.has_resources(di):
            self.deduct_resources(di)

    def free_space_of_resource(self, res_type) -> int:
        """возвращает число - сколько еще может вместить указанного ресурса"""
        return self.capacity.get(res_type, 0) - self.get(res_type, 0)

    def free_space_of_resources(self, di: dict) -> dict[str, int]:
        """возвращает словарь со свободными местами для всех ресурсов из di"""
        return dict({key: self.capacity.get(key, 0) - self.get(key, 0) for key, val in di.items()})

    def add_resources(self, di: dict):
        """добавляет ресурсы в хранилище"""
        for key, val in di.items():
            self[di] += val

    def can_afford(self, core_resources: Dict[str, int]) -> bool:
        """
        Проверяет, хватает ли ресурсов в ядре для оплаты стоимости

        Параметры:
        core_resources: Dict[str, int] - текущие ресурсы ядра в формате {'Медь': 5, 'Олово': 3}

        Возвращает:
        bool - True если всех ресурсов достаточно, False если хотя бы одного не хватает
        """
        return all(core_resources.get(key, 0) <= val for key, val in self.cost.items()) # Оставлю на всякий случай

    def deduct_from_core(self, core: 'Core'):
        """
        Вычитает стоимость из ядра

        Параметры:
        core: Core - объект ядра

        Возвращает:
        bool - True при успехе, False если недостаточно ресурсов

        Логика:
        - Проверяет can_afford()
        - При успехе вычитает ресурсы из core.resources
        - Возвращает результат операции
        """
        if self.can_afford(core.resources):
            for resource_name, amount in self.cost.items():
                core.resources[resource_name] -= amount

    def refund_half_to_core(self, core: 'Core'):
        """
        Возвращает половину стоимости в ядро при сносе здания

        Параметры:
        core: Core - объект ядра

        Логика:
        - Для каждого ресурса вычисляет половину стоимости (округление вниз)
        - Добавляет полученное количество в core.resources
        - Пример: стоимость [[3, 'Медь']] вернет 1 Медь (3//2 = 1)
        """
        for resource_name, amount in self.cost.items():
            core.resources[resource_name] += amount // 2


class Core(arcade.Sprite):
    """Ядро - центральный объект, который нужно защитить"""

    def __init__(self, filename: str, scale: float, x: float, y: float):
        """
        Инициализация ядра

        Параметры:
        filename: str - путь к изображению ядра (32x32 пикселей)
        scale: float - масштаб изображения (0.5 для получения 16px)
        x: float - позиция X центра ядра в пикселях
        y: float - позиция Y центра ядра в пикселях

        Атрибуты:
        self.size: int = 2 - размер в клетках (2x2)
        self.hp: int = 20 - здоровье ядра
        self.max_hp: int = 20 - максимальное здоровье
        self.name: str = "Ядро" - название для UI
        self.resources: Dict[str, int] - словарь ресурсов ядра
            Формат: {"Медь": 10, "Олово": 5, "Уголь": 5, ...}
        """
        super().__init__(filename, scale)
        self.center_x = x
        self.center_y = y
        self.size = 2
        self.hp = 20
        self.max_hp = 20
        self.name = "Ядро"
        self.resources = {
            "Медь": 10,
            "Олово": 5,
            "Уголь": 5,
            "Бронза": 0,
            "Кремний": 0,
            "Микросхема": 0,
            "Боеприпасы": 0
        }

    def add_resource(self, resource_type: str, amount: int = 1):
        """
        Добавляет ресурс в ядро

        Параметры:
        resource_type: str - тип ресурса ('Медь', 'Олово' и т.д.)
        amount: int = 1 - количество для добавления

        Логика:
        - Ядро имеет бесконечное хранилище
        - Просто увеличивает счетчик ресурса
        - Если ресурса еще нет в словаре - создает его
        """
        self.resources[resource_type] = self.resources.get(resource_type, 0) + amount

    def get_resource_count(self, resource_type: str) -> int:
        """
        Получает количество ресурса в ядре

        Параметры:
        resource_type: str - тип ресурса

        Возвращает:
        int - количество ресурса (0 если такого ресурса нет)
        """
        return self.resources.get(resource_type, 0)

    def take_damage(self, amount: int):
        """
        Наносит урон ядру

        Параметры:
        amount: int - количество урона

        Логика:
        - Уменьшает HP на amount
        - Если HP становится <= 0 - ядро уничтожено
        - Не позволяет HP быть меньше 0
        """
        self.hp -= amount
        if self.hp <= 0:
            self.hp = 0  # Game over

    def deduct_one_of_each_resource(self):
        """
        Вычитает по одному ресурсу каждого доступного вида

        Логика:
        - Для каждого типа ресурса в RESOURCES:
          * Если ресурса > 0 - вычитает 1
          * Если ресурса = 0 - пропускает
        - Используется при восстановлении дронов
        - Если не хватает ресурсов - вычитает столько, сколько есть
        """
        for res in self.resources.keys():
            if self.resources.get(res, 0) > 0:
                self.resources[res] -= 1
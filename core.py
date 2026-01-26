# core.py
import arcade
from typing import List, Dict, Union, Optional


class ResourceCost:
    """Класс для представления стоимости построек в ресурсах"""

    def __init__(self, cost_list: List[List[Union[int, str]]]):
        """
        Инициализация стоимости здания

        Параметры:
        cost_list: List[List[Union[int, str]]] - список вида [[количество, 'ресурс']]
            Пример: [[2, 'Медь'], [1, 'Олово']]

        Атрибуты:
        self.cost_list: List[List[Union[int, str]]] - исходный список стоимости
        self.cost_dict: Dict[str, int] - словарь для быстрого доступа {'Медь': 2, 'Олово': 1}
        """
        self.cost_list = cost_list
        self.cost_dict = {}
        for amount, resource_name in cost_list:
            self.cost_dict[resource_name] = amount

    def can_afford(self, core_resources: Dict[str, int]) -> bool:
        """
        Проверяет, хватает ли ресурсов в ядре для оплаты стоимости

        Параметры:
        core_resources: Dict[str, int] - текущие ресурсы ядра в формате {'Медь': 5, 'Олово': 3}

        Возвращает:
        bool - True если всех ресурсов достаточно, False если хотя бы одного не хватает
        """
        for resource_name, amount in self.cost_dict.items():
            if core_resources.get(resource_name, 0) < amount:
                return False
        return True

    def deduct_from_core(self, core: 'Core') -> bool:
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
            for resource_name, amount in self.cost_dict.items():
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
        for resource_name, amount in self.cost_dict.items():
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
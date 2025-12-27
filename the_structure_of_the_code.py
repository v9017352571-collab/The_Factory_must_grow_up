import arcade
from arcade.gui import UIManager, UIDropdown, UIFlatButton
from typing import Optional, Dict, List, Tuple, Any, Union
import random


class ResourceCost:
    """Класс для представления стоимости построек в ресурсах"""

    def __init__(self, cost_list: List[List[Union[int, str]]]):
        """
        Инициализация стоимости здания

        Параметры:
        cost_list: List[List[Union[int, str]]] - список списков вида [[количество1, 'ресурс1'], [количество2, 'ресурс2']]
        Пример: [[10, 'Медь'], [5, 'Кремний']]

        Атрибуты:
        self.cost_list: List[List[Union[int, str]]] - исходный список стоимости
        self.cost_dict: Dict[str, int] - словарь для удобного доступа {'Медь': 10, 'Кремний': 5}
        """
        self.cost_list = cost_list
        self.cost_dict = {}
        for amount, resource_name in cost_list:
            self.cost_dict[resource_name] = amount

    def can_afford(self, core_resources: Dict[str, int]) -> bool:
        pass
        # Проверяет, хватает ли ресурсов в ядре для оплаты стоимости
        # Возвращает True если всех ресурсов достаточно, False если хотя бы одного не хватает

    def deduct_from_core(self, core: 'Core') -> bool:
        pass
        # Вычитает стоимость из ядра
        # Возвращает True при успехе, False если недостаточно ресурсов

    def refund_half_to_core(self, core: 'Core'):
        pass
        # Возвращает половину стоимости в ядро при сносе здания
        # Округление в меньшую сторону


class Building(arcade.Sprite):
    def __init__(self, filename: str, scale: float, x: float, y: float, size: int = 1,
                 resource_capacity: Optional[Dict[str, int]] = None,
                 cost: ResourceCost = None, name: str = "Здание"):
        """
        Базовый класс для всех построек

        Параметры:
        filename: str - путь к файлу изображения здания (32x32 пикселей)
        scale: float - масштаб изображения (для 32px спрайтов используем scale=0.5, чтобы получить 16px)
        x: float - позиция X в пикселях (центр здания)
        y: float - позиция Y в пикселях (центр здания)
        size: int = 1 - размер здания в клетках (все здания квадратные)
        resource_capacity: Optional[Dict[str, int]] = None - вместимость ресурсов {'Уголь': 1, 'Камень': 1}
        cost: ResourceCost = None - стоимость постройки, если None то базовая стоимость 1 Медь
        name: str = "Здание" - название здания для отображения при наведении

        Атрибуты:
        self.size: int - размер здания в клетках (квадратное)
        self.rotation_side: int = 0 - текущее направление поворота (0-вверх, 1-вправо, 2-вниз, 3-влево)
        self.resources: Dict[str, int] - текущие ресурсы внутри здания {'Уголь': 1, 'Песок': 0}
        self.infinite_storage: bool - флаг бесконечного хранилища
        self.name: str - название здания для UI
        self.hp: int = 5 - прочность здания
        self.max_hp: int = 5 - максимальная прочность
        """
        super().__init__(filename, scale)
        self.center_x = x
        self.center_y = y
        self.size = size
        self.rotation_side = 0
        self.name = name
        self.hp = 5
        self.max_hp = 5

        # Стоимость постройки - по умолчанию 1 Медь
        if cost is None:
            self.cost = ResourceCost([[1, 'Медь']])
        else:
            self.cost = cost

        # Система хранения ресурсов
        self.resources: Dict[str, int] = {}
        if resource_capacity is None:
            self.infinite_storage = True
            self.resource_capacity = {}
        else:
            self.infinite_storage = False
            self.resource_capacity = resource_capacity.copy()
            for res in self.resource_capacity:
                self.resources[res] = 0

    def can_accept(self, resource_type: str) -> bool:
        pass
        # Проверяет, может ли здание принять ресурс указанного типа
        # Возвращает True если может принять, False если не может

    def accept_resource(self, resource_type: str) -> bool:
        pass
        # Принимает ресурс указанного типа
        # Возвращает True если успешно принял, False если не смог
        # Для зданий с "any" вместимостью - принимает любой ресурс
        # Для обычных зданий - увеличивает счетчик конкретного ресурса

    def has_resource(self, resource_type: str) -> bool:
        pass
        # Проверяет наличие хотя бы одной единицы ресурса
        # Возвращает True если есть хотя бы один, False если нет или ноль

    def consume_resource(self, resource_type: str, amount: int = 1) -> bool:
        pass
        # Потребляет ресурс для производства
        # Возвращает True если успешно потребил, False если недостаточно
        # Уменьшает количество ресурса на amount

    def produce_output(self) -> Optional[str]:
        pass
        # Производит и пытается передать ресурс
        # Вызывает внутренние методы для производства и передачи
        # Возвращает тип переданного ресурса или None

    def transfer_resources(self, adjacent_buildings: Dict[int, 'Building'], delta_time: float):
        pass
        # Обрабатывает передачу ресурсов соседним зданиям
        # adjacent_buildings: Dict[int, 'Building'] - словарь соседей {направление: здание}
        # delta_time: float - время с последнего кадра для синхронизации
        # Вызывается из основного цикла игры

    def get_receiving_side(self) -> int:
        pass
        # Возвращает направление принимающей стороны
        # Для большинства зданий - противоположное выходной стороне
        # Для роутера и перекрестка - особая логика

    def rotate(self):
        pass
        # Поворачивает здание на 90 градусов по часовой стрелке
        # Увеличивает rotation_side на 1, сбрасывает в 0 при достижении 4
        # Не меняет текстуру, только логическое направление

    def take_damage(self, amount: int):
        pass
        # Наносит урон зданию
        # Уменьшает HP на amount
        # Если HP <= 0 - здание уничтожается, все ресурсы исчезают

    def can_build(self, core: 'Core') -> bool:
        pass
        # Проверяет, может ли игрок построить это здание
        # Возвращает True если можно построить, False если не хватает ресурсов


class Core(arcade.Sprite):
    def __init__(self, filename: str, scale: float, x: float, y: float):
        """
        Класс ядра - центральный объект, который нужно защитить

        Параметры:
        filename: str - путь к изображению ядра (32x32 пикселей)
        scale: float - масштаб (scale=0.5 для 16px)
        x: float - позиция X в пикселях (центр ядра)
        y: float - позиция Y в пикселях (центр ядра)

        Особенности:
        - Размер 2x2 клетки (32x32 пикселей в мире)
        - Бесконечное хранилище всех ресурсов
        - Высокое HP (20)
        - Начальные ресурсы для постройки первых зданий

        Атрибуты:
        self.hp: int = 20 - здоровье ядра
        self.max_hp: int = 20 - максимальное здоровье
        self.resources: Dict[str, int] - словарь ресурсов ядра
        self.size: int = 2 - размер в клетках
        self.name: str = "Ядро" - название для UI
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
            "Олово и свинец": 0,
            "Уголь": 5,
            "Камень": 5,
            "Железо": 0,
            "Железная руда": 0,
            "Кирпич": 0,
            "Бронза": 0,
            "Песок": 0,
            "Кремний": 0,
            "Микросхема": 0,
            "Компьютер": 0
        }

    def add_resource(self, resource_type: str, amount: int = 1):
        pass
        # Добавляет ресурс в ядро
        # Ядро имеет бесконечное хранилище
        # Просто увеличивает счетчик ресурса

    def get_resource_count(self, resource_type: str) -> int:
        pass
        # Получает количество ресурса в ядре
        # Возвращает количество ресурса (0 если нет такого ресурса)

    def take_damage(self, amount: int):
        pass
        # Наносит урон ядру
        # Уменьшает HP на amount
        # Если HP <= 0 - ядро уничтожено


class MineDrill(Building):
    def __init__(self, filename: str, scale: float, x: float, y: float, mineable_resources: List[str],
                 fuel_required: bool = True):
        """
        Базовый класс для буров (шахт)

        Параметры:
        filename: str - путь к изображению (32x32 пикселей)
        scale: float - масштаб (scale=0.5 для 16px)
        x: float - позиция X в пикселях
        y: float - позиция Y в пикселях
        mineable_resources: List[str] - список ресурсов, которые можно добывать
        fuel_required: bool = True - требуется ли уголь для работы

        Особенности:
        - Размер 2x2 клетки
        - Добывает ресурсы из земли
        - Может требовать уголь для работы
        """
        capacity = {"Уголь": 1} if fuel_required else {}
        cost = ResourceCost([[2, 'Медь'], [1, 'Камень']])
        super().__init__(filename, scale, x, y, size=2, resource_capacity=capacity, cost=cost, name="Бур")
        self.mineable_resources = mineable_resources
        self.fuel_required = fuel_required
        self.production_timer = 0.0
        self.production_interval = 1.0  # 1 секунда


class CoalDrill(MineDrill):
    def __init__(self, filename: str, scale: float, x: float, y: float):
        """
        Угольный бур - может добывать все руды кроме железной, потребляет уголь

        Параметры:
        filename: str - путь к изображению
        scale: float - масштаб (scale=0.5 для 16px)
        x: float - позиция X в пикселях
        y: float - позиция Y в пикселях

        Особенности:
        - Добывает: Олово и свинец, Медь, Уголь, Камень
        - Требует уголь для работы
        - Стоимость: 2 Медь + 1 Камень
        """
        super().__init__(filename, scale, x, y,
                         ["Олово и свинец", "Медь", "Уголь", "Камень"],
                         fuel_required=True)


class ElectricDrill(MineDrill):
    def __init__(self, filename: str, scale: float, x: float, y: float):
        """
        Электрический бур - может добывать все руды очень быстро, ничего не потребляет

        Параметры:
        filename: str - путь к изображению
        scale: float - масштаб (scale=0.5 для 16px)
        x: float - позиция X в пикселях
        y: float - позиция Y в пикселях

        Особенности:
        - Добывает: все руды включая железную
        - Не требует ресурсов для работы
        - Работает быстрее (0.5 секунды на ресурс)
        - Стоимость: 3 Медь + 1 Железо
        """
        super().__init__(filename, scale, x, y,
                         ["Олово и свинец", "Медь", "Уголь", "Камень", "Железная руда"],
                         fuel_required=False)
        self.production_interval = 0.5  # 0.5 секунды


class Conveyor(Building):
    def __init__(self, filename: str, scale: float, x: float, y: float):
        """
        Конвейер - перемещает ресурсы между зданиями

        Параметры:
        filename: str - путь к изображению
        scale: float - масштаб (scale=0.5 для 16px)
        x: float - позиция X в пикселях
        y: float - позиция Y в пикселях

        Особенности:
        - Размер 1x1 клетка
        - Вместимость: 1 любой ресурс
        - Стоимость: 1 Медь
        """
        super().__init__(filename, scale, x, y, size=1,
                         resource_capacity={"any": 1},
                         cost=ResourceCost([[1, 'Медь']]),
                         name="Конвейер")


class Router(Building):
    def __init__(self, filename: str, scale: float, x: float, y: float):
        """
        Маршрутизатор - распределяет ресурсы по разным направлениям

        Параметры:
        filename: str - путь к изображению
        scale: float - масштаб (scale=0.5 для 16px)
        x: float - позиция X в пикселях
        y: float - позиция Y в пикселях

        Особенности:
        - Размер 1x1 клетка
        - Вместимость: 1 любой ресурс
        - По умолчанию распределяет рандомно
        - Стоимость: 2 Медь
        """
        super().__init__(filename, scale, x, y, size=1,
                         resource_capacity={"any": 1},
                         cost=ResourceCost([[2, 'Медь']]),
                         name="Маршрутизатор")
        self.routing_rules: Dict[str, int] = {}
        self.is_configuring = False
        self.receiving_side = 0  # только одна сторона приема


class Junction(Building):
    def __init__(self, filename: str, scale: float, x: float, y: float):
        """
        Перекресток - соединяет потоки в разных направлениях

        Параметры:
        filename: str - путь к изображению
        scale: float - масштаб (scale=0.5 для 16px)
        x: float - позиция X в пикселях
        y: float - позиция Y в пикселях

        Особенности:
        - Размер 1x1 клетка
        - Вместимость: 1 любой ресурс
        - Режимы работы: HV (горизонталь-вертикаль), VH (вертикаль-горизонталь)
        - Стоимость: 3 Медь
        """
        super().__init__(filename, scale, x, y, size=1,
                         resource_capacity={"any": 1},
                         cost=ResourceCost([[3, 'Медь']]),
                         name="Перекресток")
        self.mode = "HV"  # "HV" или "VH"
        self.is_configuring = False


class StoneFurnace(Building):
    def __init__(self, filename: str, scale: float, x: float, y: float):
        """
        Печь для обжига камня - производит кирпичи из камня и угля

        Параметры:
        filename: str - путь к изображению
        scale: float - масштаб (scale=0.5 для 16px)
        x: float - позиция X в пикселях
        y: float - позиция Y в пикселях

        Особенности:
        - Размер 2x2 клетки
        - Вход: 1 Камень + 1 Уголь
        - Выход: 1 Кирпич
        - Стоимость: 2 Медь + 1 Камень
        """
        super().__init__(filename, scale, x, y, size=2,
                         resource_capacity={"Камень": 1, "Уголь": 1},
                         cost=ResourceCost([[2, 'Медь'], [1, 'Камень']]),
                         name="Печь для камня")
        self.input_resources = {"Камень": 1, "Уголь": 1}
        self.output_resource = "Кирпич"
        self.production_timer = 0.0
        self.production_interval = 1.0


class BronzeFurnace(Building):
    def __init__(self, filename: str, scale: float, x: float, y: float):
        """
        Печь для бронзы - производит бронзу из олова и меди

        Параметры:
        filename: str - путь к изображению
        scale: float - масштаб (scale=0.5 для 16px)
        x: float - позиция X в пикселях
        y: float - позиция Y в пикселях

        Особенности:
        - Размер 2x2 клетки
        - Вход: 1 Олово и свинец + 1 Медь
        - Выход: 1 Бронза
        - Стоимость: 3 Медь
        """
        super().__init__(filename, scale, x, y, size=2,
                         resource_capacity={"Олово и свинец": 1, "Медь": 1},
                         cost=ResourceCost([[3, 'Медь']]),
                         name="Печь для бронзы")
        self.input_resources = {"Олово и свинец": 1, "Медь": 1}
        self.output_resource = "Бронза"
        self.production_timer = 0.0
        self.production_interval = 1.0


class Crusher(Building):
    def __init__(self, filename: str, scale: float, x: float, y: float):
        """
        Дробитель - производит песок из камня и угля

        Параметры:
        filename: str - путь к изображению
        scale: float - масштаб (scale=0.5 для 16px)
        x: float - позиция X в пикселях
        y: float - позиция Y в пикселях

        Особенности:
        - Размер 1x1 клетка
        - Вход: 1 Камень + 1 Уголь
        - Выход: 1 Песок
        - Стоимость: 2 Медь + 1 Камень
        """
        super().__init__(filename, scale, x, y, size=1,
                         resource_capacity={"Камень": 1, "Уголь": 1},
                         cost=ResourceCost([[2, 'Медь'], [1, 'Камень']]),
                         name="Дробитель")
        self.input_resources = {"Камень": 1, "Уголь": 1}
        self.output_resource = "Песок"
        self.production_timer = 0.0
        self.production_interval = 1.0


class SiliconFurnace(Building):
    def __init__(self, filename: str, scale: float, x: float, y: float):
        """
        Кремневая печь - производит кремний из песка и угля

        Параметры:
        filename: str - путь к изображению
        scale: float - масштаб (scale=0.5 для 16px)
        x: float - позиция X в пикселях
        y: float - позиция Y в пикселях

        Особенности:
        - Размер 2x2 клетки
        - Вход: 1 Песок + 1 Уголь
        - Выход: 1 Кремний
        - Стоимость: 3 Медь + 1 Песок
        """
        super().__init__(filename, scale, x, y, size=2,
                         resource_capacity={"Песок": 1, "Уголь": 1},
                         cost=ResourceCost([[3, 'Медь'], [1, 'Песок']]),
                         name="Кремневая печь")
        self.input_resources = {"Песок": 1, "Уголь": 1}
        self.output_resource = "Кремний"
        self.production_timer = 0.0
        self.production_interval = 1.0


class CircuitFactory(Building):
    def __init__(self, filename: str, scale: float, x: float, y: float):
        """
        Производство микросхем - производит микросхемы из меди, олово-свинца и кремния

        Параметры:
        filename: str - путь к изображению
        scale: float - масштаб (scale=0.5 для 16px)
        x: float - позиция X в пикселях
        y: float - позиция Y в пикселях

        Особенности:
        - Размер 3x3 клетки
        - Вход: 1 Медь + 1 Олово и свинец + 1 Кремний
        - Выход: 1 Микросхема
        - Стоимость: 5 Медь + 2 Кремний
        """
        super().__init__(filename, scale, x, y, size=3,
                         resource_capacity={"Медь": 1, "Олово и свинец": 1, "Кремний": 1},
                         cost=ResourceCost([[5, 'Медь'], [2, 'Кремний']]),
                         name="Производство микросхем")
        self.input_resources = {"Медь": 1, "Олово и свинец": 1, "Кремний": 1}
        self.output_resource = "Микросхема"
        self.production_timer = 0.0
        self.production_interval = 1.0


class BlastFurnace(Building):
    def __init__(self, filename: str, scale: float, x: float, y: float):
        """
        Доменная печь - производит железо из железной руды и угля

        Параметры:
        filename: str - путь к изображению
        scale: float - масштаб (scale=0.5 для 16px)
        x: float - позиция X в пикселях
        y: float - позиция Y в пикселях

        Особенности:
        - Размер 2x2 клетки
        - Вход: 1 Железная руда + 1 Уголь
        - Выход: 1 Железо
        - Стоимость: 4 Медь + 1 Уголь
        """
        super().__init__(filename, scale, x, y, size=2,
                         resource_capacity={"Железная руда": 1, "Уголь": 1},
                         cost=ResourceCost([[4, 'Медь'], [1, 'Уголь']]),
                         name="Доменная печь")
        self.input_resources = {"Железная руда": 1, "Уголь": 1}
        self.output_resource = "Железо"
        self.production_timer = 0.0
        self.production_interval = 1.0


class ComputerFactory(Building):
    def __init__(self, filename: str, scale: float, x: float, y: float):
        """
        Производство компьютеров - производит компьютеры из меди, олово-свинца, железа и микросхем

        Параметры:
        filename: str - путь к изображению
        scale: float - масштаб (scale=0.5 для 16px)
        x: float - позиция X в пикселях
        y: float - позиция Y в пикселях

        Особенности:
        - Размер 3x3 клетки
        - Вход: 1 Медь + 1 Олово и свинец + 1 Железо + 1 Микросхема
        - Выход: 1 Компьютер
        - Стоимость: 8 Медь + 3 Железо + 2 Микросхема
        """
        super().__init__(filename, scale, x, y, size=3,
                         resource_capacity={"Медь": 1, "Олово и свинец": 1, "Железо": 1, "Микросхема": 1},
                         cost=ResourceCost([[8, 'Медь'], [3, 'Железо'], [2, 'Микросхема']]),
                         name="Производство компьютеров")
        self.input_resources = {"Медь": 1, "Олово и свинец": 1, "Железо": 1, "Микросхема": 1}
        self.output_resource = "Компьютер"
        self.production_timer = 0.0
        self.production_interval = 1.0


class Turret(Building):
    def __init__(self, base_filename: str, tower_filename: str, scale: float,
                 x: float, y: float, size: int, damage: int, range_: float,
                 cooldown: float, ammo_requirements: Dict[str, int]):
        """
        Турель - состоит из двух текстур: неподвижной основы и подвижной башни

        Параметры:
        base_filename: str - путь к изображению основы
        tower_filename: str - путь к изображению башни
        scale: float - масштаб (scale=0.5 для 16px)
        x: float - позиция X в пикселях
        y: float - позиция Y в пикселях
        size: int - размер в клетках
        damage: int - урон по врагам
        range_: float - дальность поражения в пикселях
        cooldown: float - время перезарядки в секундах
        ammo_requirements: Dict[str, int] - требуемые боеприпасы {'Камень': 1}

        Атрибуты:
        self.base_sprite: arcade.Sprite - неподвижная основа
        self.tower_sprite: arcade.Sprite - подвижная башня
        self.bullet_list: arcade.SpriteList - список пуль
        self.current_cooldown: float = 0.0 - текущее время перезарядки
        """
        super().__init__(base_filename, scale, x, y, size,
                         ammo_requirements,
                         ResourceCost([[1, 'Медь']]),
                         name="Турель")

        # Неподвижная основа
        self.base_sprite = arcade.Sprite(base_filename, scale)
        self.base_sprite.center_x = x
        self.base_sprite.center_y = y

        # Подвижная башня
        self.tower_sprite = arcade.Sprite(tower_filename, scale)
        self.tower_sprite.center_x = x
        self.tower_sprite.center_y = y

        # Параметры стрельбы
        self.damage = damage
        self.range = range_
        self.max_cooldown = cooldown
        self.current_cooldown = 0.0
        self.ammo_requirements = ammo_requirements
        self.bullet_list = arcade.SpriteList()
        self.target = None


class SlingshotTurret(Turret):
    def __init__(self, base_filename: str, tower_filename: str, scale: float, x: float, y: float):
        """
        Рогаточная турель - самая слабая турель

        Параметры:
        base_filename: str - путь к изображению основы
        tower_filename: str - путь к изображению башни
        scale: float - масштаб (scale=0.5 для 16px)
        x: float - позиция X в пикселях
        y: float - позиция Y в пикселях

        Особенности:
        - Размер 2x2 клетки
        - Боеприпасы: 1 Камень
        - Урон: 1
        - Дальность: 48 пикселей (3 блока)
        - Перезарядка: 3 секунды
        - Стоимость: 1 Медь + 1 Камень
        """
        super().__init__(base_filename, tower_filename, scale, x, y, size=2,
                         damage=1, range_=48.0, cooldown=3.0,
                         ammo_requirements={"Камень": 1})


class CannonTurret(Turret):
    def __init__(self, base_filename: str, tower_filename: str, scale: float, x: float, y: float):
        """
        Пушечная турель - средняя турель

        Параметры:
        base_filename: str - путь к изображению основы
        tower_filename: str - путь к изображению башни
        scale: float - масштаб (scale=0.5 для 16px)
        x: float - позиция X в пикселях
        y: float - позиция Y в пикселях

        Особенности:
        - Размер 2x2 клетки
        - Боеприпасы: 1 Олово и свинец + 1 Уголь
        - Урон: 2
        - Дальность: 80 пикселей (5 блоков)
        - Перезарядка: 2 секунды
        - Стоимость: 2 Медь + 1 Олово и свинец + 1 Уголь
        """
        super().__init__(base_filename, tower_filename, scale, x, y, size=2,
                         damage=2, range_=80.0, cooldown=2.0,
                         ammo_requirements={"Олово и свинец": 1, "Уголь": 1})


class MachineGunTurret(Turret):
    def __init__(self, base_filename: str, tower_filename: str, scale: float, x: float, y: float):
        """
        Пулеметная турель - быстрая турель с низким уроном

        Параметры:
        base_filename: str - путь к изображению основы
        tower_filename: str - путь к изображению башни
        scale: float - масштаб (scale=0.5 для 16px)
        x: float - позиция X в пикселях
        y: float - позиция Y в пикселях

        Особенности:
        - Размер 3x3 клетки
        - Боеприпасы: 1 Олово и свинец + 1 Бронза + 1 Уголь
        - Урон: 2
        - Дальность: 48 пикселей (3 блока)
        - Перезарядка: 1 секунда
        - Стоимость: 3 Медь + 1 Олово и свинец + 1 Бронза + 1 Уголь
        """
        super().__init__(base_filename, tower_filename, scale, x, y, size=3,
                         damage=2, range_=48.0, cooldown=1.0,
                         ammo_requirements={"Олово и свинец": 1, "Бронза": 1, "Уголь": 1})


class LongRangeTurret(Turret):
    def __init__(self, base_filename: str, tower_filename: str, scale: float, x: float, y: float):
        """
        Длинноствольная турель - мощная турель с хорошей дальностью

        Параметры:
        base_filename: str - путь к изображению основы
        tower_filename: str - путь к изображению башни
        scale: float - масштаб (scale=0.5 для 16px)
        x: float - позиция X в пикселях
        y: float - позиция Y в пикселях

        Особенности:
        - Размер 2x2 клетки
        - Боеприпасы: 1 Железо + 1 Уголь
        - Урон: 3
        - Дальность: 80 пикселей (5 блоков)
        - Перезарядка: 2 секунды
        - Стоимость: 3 Медь + 1 Железо + 1 Уголь
        """
        super().__init__(base_filename, tower_filename, scale, x, y, size=2,
                         damage=3, range_=80.0, cooldown=2.0,
                         ammo_requirements={"Железо": 1, "Уголь": 1})


class RocketTurret(Turret):
    def __init__(self, base_filename: str, tower_filename: str, scale: float, x: float, y: float):
        """
        Ракетная турель - самая мощная турель

        Параметры:
        base_filename: str - путь к изображению основы
        tower_filename: str - путь к изображению башни
        scale: float - масштаб (scale=0.5 для 16px)
        x: float - позиция X в пикселях
        y: float - позиция Y в пикселях

        Особенности:
        - Размер 3x3 клетки
        - Боеприпасы: 1 Компьютер + 1 Железо + 1 Уголь
        - Урон: 3
        - Дальность: 112 пикселей (7 блоков)
        - Перезарядка: 3 секунды
        - Стоимость: 5 Медь + 2 Железо + 1 Компьютер + 1 Уголь
        """
        super().__init__(base_filename, tower_filename, scale, x, y, size=3,
                         damage=3, range_=112.0, cooldown=3.0,
                         ammo_requirements={"Компьютер": 1, "Железо": 1, "Уголь": 1})


class Bullet(arcade.Sprite):
    def __init__(self, filename: str, scale: float, damage: int, lifetime: float,
                 source: Any, target: Any):
        """
        Класс пули

        Параметры:
        filename: str - путь к изображению пули (32x32 пикселей)
        scale: float - масштаб (scale=0.5 для 16px)
        damage: int - урон от пули
        lifetime: float - время жизни в секундах
        source: Any - источник выстрела (турель или жук)
        target: Any - цель выстрела (жук, ядро, игрок)

        Атрибуты:
        self.damage: int - урон
        self.lifetime: float - оставшееся время жизни в секундах
        self.max_lifetime: float - максимальное время жизни
        self.source: Any - источник
        self.target: Any - цель
        self.speed: float = 300.0 - скорость пули в пикселях в секунду
        """
        super().__init__(filename, scale)
        self.damage = damage
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.source = source
        self.target = target
        self.speed = 300.0


class Bug(arcade.Sprite):
    def __init__(self, filename: str, scale: float, hp: int, damage: int, speed: float,
                 is_ranged: bool, name: str = "Жук"):
        """
        Базовый класс для врагов

        Параметры:
        filename: str - путь к изображению жука (32x32 пикселей)
        scale: float - масштаб (scale=0.5 для 16px)
        hp: int - здоровье жука
        damage: int - урон по целям
        speed: float - скорость в блоках в секунду
        is_ranged: bool - является ли дальнобойным
        name: str = "Жук" - название для отладки

        Атрибуты:
        self.speed_pixels: float - скорость в пикселях в секунду (блок = 16 пикселей)
        self.is_ranged: bool - флаг дальнобойной атаки
        self.bullet_list: arcade.SpriteList - список пуль
        self.target: Any = None - текущая цель
        self.attack_cooldown: float = 0.0 - таймер атаки в секундах
        """
        super().__init__(filename, scale)
        self.hp = hp
        self.max_hp = hp
        self.damage = damage
        self.speed = speed
        self.speed_pixels = speed * 16.0
        self.is_ranged = is_ranged
        self.name = name
        self.bullet_list = arcade.SpriteList()
        self.target = None
        self.attack_cooldown = 0.0

    def update(self, delta_time: float):
        pass
        # Обновление состояния жука с учетом delta_time

    def attack_target(self):
        pass
        # Атака цели
        # Мгновенно наносит урон
        # Для ranged создает пулю вместо прямого урона
        # Сбрасывает attack_cooldown = 0 (мгновенно по ТЗ)


class Beetle(Bug):
    def __init__(self, filename: str, scale: float):
        """
        Обычный жук: низкий урон, низкий хп, высокая скорость, ближник

        Параметры:
        filename: str - путь к изображению
        scale: float - масштаб (scale=0.5 для 16px)

        Статистики:
        hp: 1
        damage: 1
        speed: 3 (3 блока/сек)
        is_ranged: False
        name: "Обычный жук"
        """
        super().__init__(filename, scale, hp=1, damage=1, speed=3.0,
                         is_ranged=False, name="Обычный жук")


class ArmoredBeetle(Bug):
    def __init__(self, filename: str, scale: float):
        """
        Жук броненосец: низкий урон, большой хп, низкая скорость, ближник

        Параметры:
        filename: str - путь к изображению
        scale: float - масштаб (scale=0.5 для 16px)

        Статистики:
        hp: 3
        damage: 1
        speed: 1 (1 блок/сек)
        is_ranged: False
        name: "Броненосец"
        """
        super().__init__(filename, scale, hp=3, damage=1, speed=1.0,
                         is_ranged=False, name="Броненосец")


class SpittingBeetle(Bug):
    def __init__(self, filename: str, scale: float):
        """
        Жук-плевок: средний урон, низкий хп, средняя скорость, дальник

        Параметры:
        filename: str - путь к изображению
        scale: float - масштаб (scale=0.5 для 16px)

        Статистики:
        hp: 1
        damage: 2
        speed: 2 (2 блока/сек)
        is_ranged: True
        name: "Жук-плевок"
        """
        super().__init__(filename, scale, hp=1, damage=2, speed=2.0,
                         is_ranged=True, name="Жук-плевок")


class DominicTorettoBeetle(Bug):
    def __init__(self, filename: str, scale: float):
        """
        Жук Доминико Торетто: средний урон, высокий хп, высокая скорость, ближник

        Параметры:
        filename: str - путь к изображению
        scale: float - масштаб (scale=0.5 для 16px)

        Статистики:
        hp: 2
        damage: 2
        speed: 3 (3 блока/сек)
        is_ranged: False
        name: "Доминико Торетто"
        """
        super().__init__(filename, scale, hp=2, damage=2, speed=3.0,
                         is_ranged=False, name="Доминико Торетто")


class HarkerBeetle(Bug):
    def __init__(self, filename: str, scale: float):
        """
        Жук-харкатель: высокий урон, средний хп, низкая скорость, дальник

        Параметры:
        filename: str - путь к изображению
        scale: float - масштаб (scale=0.5 для 16px)

        Статистики:
        hp: 2
        damage: 3
        speed: 1 (1 блок/сек)
        is_ranged: True
        name: "Жук-харкатель"
        """
        super().__init__(filename, scale, hp=2, damage=3, speed=1.0,
                         is_ranged=True, name="Жук-харкатель")


class Player(arcade.Sprite):
    def __init__(self, filename: str, scale: float, core: Core):
        """
        Класс игрока - космический аппарат

        Параметры:
        filename: str - путь к изображению игрока (32x32 пикселей)
        scale: float - масштаб (scale=0.5 для 16px)
        core: Core - ссылка на ядро для возрождения

        Атрибуты:
        self.core: Core - ссылка на ядро
        self.hp: int = 3 - здоровье игрока
        self.max_hp: int = 3 - максимальное здоровье
        self.speed: float = 16.0 - скорость в пикселях в секунду
        self.is_dead: bool = False - флаг смерти
        self.respawn_timer: float = 0.0 - таймер возрождения в секундах
        self.max_respawn_timer: float = 5.0 - 5 секунд на возрождение
        """
        super().__init__(filename, scale)
        self.core = core
        self.hp = 3
        self.max_hp = 3
        self.speed = 16.0
        self.is_dead = False
        self.respawn_timer = 0.0
        self.max_respawn_timer = 5.0
        self.center_x = core.center_x
        self.center_y = core.center_y + core.height + 32

    def update(self, delta_time: float):
        pass
        # Обновление состояния игрока с учетом delta_time

    def respawn(self, map_height_pixels: int):
        pass
        # Возрождение игрока
        # x = core.center_x
        # y = map_height_pixels - 8


class MyGame(arcade.Window):
    def __init__(self, width: int, height: int, title: str, map_filename: str):
        """
        Основной класс игры

        Параметры:
        width: int - ширина окна в пикселях
        height: int - высота окна в пикселях
        title: str - заголовок окна
        map_filename: str - путь к файлу карты JSON

        Атрибуты:
        self.ui_manager: UIManager - менеджер пользовательского интерфейса
        self.world_camera: Camera2D - камера для мира (следует за игроком)
        self.gui_camera: Camera2D - камера для UI (статичная)
        self.player: Player - объект игрока
        self.core: Core - объект ядра
        self.buildings: arcade.SpriteList - список всех зданий
        self.bullets: arcade.SpriteList - список всех пуль
        self.bugs: arcade.SpriteList - список всех жуков
        self.grid: List[List[Optional[Building]]] - сетка карты
        self.map_width: int - ширина карты в клетках
        self.map_height: int - высота карты в клетках
        self.map_width_pixels: int - ширина карты в пикселях
        self.map_height_pixels: int - высота карты в пикселях
        self.tile_size: int = 16 - размер клетки в пикселях
        self.resource_transfer_accumulator: float = 0.0 - накопитель для передачи ресурсов
        self.resource_transfer_interval: float = 1.0 - интервал передачи в секундах
        self.waves: List[List[str]] - список волн (VOLN)
        self.current_wave_index: int = 0 - текущая волна
        self.wave_timer: float = 0.0 - таймер между волнами в секундах
        self.wave_interval: float = 180.0 - интервал между волнами в секундах (3 минуты)
        self.spawn_point: Tuple[int, int] - точка спавна врагов (вверху карты над ядром)
        self.selected_building_type: Optional[type] = None - выбранный тип здания для постройки
        self.hovered_building: Optional[Building] = None - здание под курсором
        self.delete_mode: bool = False - режим сноса зданий
        self.game_state: str = "playing" - состояние игры ("playing", "game_over", "victory")
        self.pressed_keys: set = set() - нажатые клавиши
        """
        super().__init__(width, height, title)
        self.ui_manager = UIManager()
        self.setup_ui()

        # Камеры
        self.world_camera = arcade.Camera2D()
        self.gui_camera = arcade.Camera2D()
        self.world_camera.viewport = (0, 0, width, height)
        self.gui_camera.viewport = (0, 0, width, height)

        # Игровые сущности
        self.player = None
        self.core = None
        self.buildings = arcade.SpriteList()
        self.bullets = arcade.SpriteList()
        self.bugs = arcade.SpriteList()

        # Карта
        self.grid = None
        self.map_width = 0
        self.map_height = 0
        self.map_width_pixels = 0
        self.map_height_pixels = 0
        self.tile_size = 16

        # Загрузка карты
        self.load_map(map_filename)

        # Система передачи ресурсов (раз в секунду)
        self.resource_transfer_accumulator = 0.0
        self.resource_transfer_interval = 1.0

        # Система волн
        self.waves = []  # будет заполнено из VOLN
        self.current_wave_index = 0
        self.wave_timer = 0.0
        self.wave_interval = 180.0  # 3 минуты = 180 секунд
        self.spawn_point = (self.map_width * 8, self.map_height_pixels - 8)  # вверху карты

        # Строительство
        self.selected_building_type = None
        self.hovered_building = None
        self.delete_mode = False

        # Состояние игры
        self.game_state = "playing"

        # Нажатые клавиши
        self.pressed_keys = set()

    def load_map(self, filename: str):
        pass
        # Загрузка карты из JSON файла

    def setup_ui(self):
        pass
        # Настройка пользовательского интерфейса

    def setup(self):
        pass
        # Инициализация игры

    def center_camera_to_player(self):
        pass
        # Центрирование камеры на игроке

    def on_update(self, delta_time: float):
        pass
        # Обновление состояния игры каждый кадр с учетом delta_time

    def on_draw(self):
        pass
        # Отрисовка игры

    def on_mouse_press(self, x: float, y: float, button: int, modifiers: int):
        pass
        # Обработка нажатия мыши

    def on_key_press(self, key: int, modifiers: int):
        pass
        # Обработка нажатия клавиш


class StartMenuWindow(arcade.Window):
    def __init__(self, width: int, height: int, title: str):
        """
        Стартовое меню игры

        Параметры:
        width: int - ширина окна
        height: int - высота окна
        title: str - заголовок окна

        Атрибуты:
        self.ui_manager: UIManager - менеджер интерфейса
        """
        super().__init__(width, height, title)
        self.ui_manager = UIManager()
        self.setup_ui()

    def setup_ui(self):
        pass
        # Настройка интерфейса стартового меню

    def start_game(self):
        pass
        # Запуск игры

    def on_draw(self):
        pass
        # Отрисовка стартового меню
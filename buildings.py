# buildings.py
import arcade
from typing import Dict, List, Optional, Any, Deque
from collections import deque
from core import ResourceCost
import random
T_SIZE = 80
BUILDING_HP = {
    "Дрон-станция": 5,
    "Угольный бур": 5,
    "Электрический бур": 5,
    "Печь для бронзы": 5,
    "Кремниевая печь": 5,
    "Завод микросхем": 5,
    "Завод боеприпасов": 5,
    "Медная турель": 5,
    "Бронзовая турель": 10,
    "Дальняя турель": 5
}

class Building(arcade.Sprite):
    """Базовый класс для всех построек"""

    def __init__(self, filename: str, scale: float, x: float, y: float, size: int = 1,
                 resource_capacity: Optional[Dict[str, int]] = None,
                 cost: ResourceCost = None, name: str = "Здание"):
        """
        Инициализация здания

        Параметры:
        filename: str - путь к изображению здания (32x32 пикселей)
        scale: float - масштаб изображения (0.5 для получения 16px)
        x: float - позиция X центра здания в пикселях
        y: float - позиция Y центра здания в пикселях
        size: int = 1 - размер здания в клетках (1x1, 2x2, 3x3)
        resource_capacity: Optional[Dict[str, int]] = None - вместимость ресурсов
        cost: ResourceCost = None - стоимость постройки, если None то 1 Медь
        name: str = "Здание" - название здания для UI

        Атрибуты:
        self.size: int - размер здания в клетках
        self.hp: int = 5 - здоровье здания
        self.max_hp: int = 5 - максимальное здоровье
        self.name: str - название для интерфейса
        self.resources: Dict[str, int] - текущие ресурсы внутри здания
        self.infinite_storage: bool = False - флаг бесконечного хранилища
        self.cost: ResourceCost - стоимость постройки
        self.output_resource: Optional[str] = None - что производит здание (для производств)
        self.waiting_drones: Deque[Drone] = deque() - очередь дронов, ждущих ресурсы
        self.waiting_for_unload: Deque[Drone] = deque() - очередь дронов, ждущих разгрузки
        """
        super().__init__(filename, scale)
        self.center_x = x
        self.center_y = y
        self.size = size
        self.name = name
        self.hp = 5
        self.max_hp = 5

        self.resource = ResourceCost(resource_capacity)

        # Система хранения ресурсов
        self.resources = {}
        self.infinite_storage = False
        self.output_resource = None  # Что производит здание

        # Очереди дронов
        self.waiting_drones = deque()  # Дроны, ждущие получения ресурса
        self.waiting_for_unload = deque()  # Дроны, ждущие разгрузки

        if resource_capacity is not None:
            self.resource_capacity = resource_capacity.copy()
            self.infinite_storage = False
            for res in self.resource_capacity:
                self.resources[res] = 0
        else:
            self.infinite_storage = True
            self.resource_capacity = {}

    def take_damage(self, amount: int):
        pass
        """
        Наносит урон зданию

        Параметры:
        amount: int - количество урона

        Логика:
        - Уменьшает HP на amount
        - Если HP становится <= 0 - здание уничтожено
        - При уничтожении все ресурсы внутри здания исчезают
        - Все дроны в очередях получают уведомление о разрушении
        - Не позволяет HP быть меньше 0
        """

    def can_accept(self, resource_type: str) -> bool:
        pass
        """
        Проверяет, может ли здание принять ресурс

        Параметры:
        resource_type: str - тип ресурса для принятия

        Возвращает:
        bool - True если здание может принять ресурс, False если не может

        Логика:
        - Если infinite_storage = True (ядро) - всегда может принять
        - Если ресурс не поддерживается этим зданием - не может принять
        - Если здание уже заполнено этим ресурсом - не может принять
        - Для производственных зданий - не может принять свой выходной ресурс
        """

    def accept_resource(self, resource_type: str) -> bool:
        pass
        """
        Принимает ресурс в здание

        Параметры:
        resource_type: str - тип ресурса для принятия

        Возвращает:
        bool - True если успешно принял, False если не смог

        Логика:
        - Сначала проверяет can_accept()
        - Увеличивает счетчик ресурса
        - Если есть дроны в waiting_for_unload - пробует отдать им ресурсы
        """

    def has_resource(self, resource_type: str) -> bool:
        pass
        """
        Проверяет наличие ресурса в здании

        Параметры:
        resource_type: str - тип ресурса

        Возвращает:
        bool - True если есть хотя бы один ресурс, False если нет
        """

    def consume_resource(self, resource_type: str, amount: int = 1) -> bool:
        pass
        """
        Потребляет ресурс из здания

        Параметры:
        resource_type: str - тип ресурса
        amount: int = 1 - количество для потребления

        Возвращает:
        bool - True если успешно потребил, False если недостаточно

        Логика:
        - Проверяет наличие ресурса
        - Уменьшает количество на amount
        - Если ресурса не хватает - возвращает False
        """

    def add_drone_to_queue(self, drone: 'Drone'):
        pass
        """
        Добавляет дрона в очередь ожидания ресурсов

        Параметры:
        drone: Drone - дрон, который хочет получить ресурс

        Логика:
        - Добавляет дрона в waiting_drones
        - Дрон будет ждать в очереди, пока не получит ресурс
        """

    def add_drone_for_unload(self, drone: 'Drone'):
        pass
        """
        Добавляет дрона в очередь ожидания разгрузки

        Параметры:
        drone: Drone - дрон, который хочет отдать ресурс

        Логика:
        - Добавляет дрона в waiting_for_unload
        - Дрон будет ждать в очереди, пока не сможет отдать ресурс
        """

    def process_queues(self, delta_time: float):
        pass
        """
        Обрабатывает очереди дронов

        Параметры:
        delta_time: float - время с предыдущего кадра

        Логика:
        - Сначала обрабатывает waiting_for_unload (разгрузка приоритетнее)
        - Затем обрабатывает waiting_drones (загрузка)
        - Для каждого дрона в очереди:
          * Проверяет расстояние до здания
          * Если дрон на расстоянии DRONE_PICKUP_DISTANCE/DRONE_DROP_DISTANCE:
            - Для waiting_drones: пытается отдать ресурс
            - Для waiting_for_unload: пытается принять ресурс
          * Если операция успешна - удаляет дрона из очереди
          * Если неуспешна - дрон остается в очереди
        """

    def can_give_resource(self) -> bool:
        pass
        """
        Проверяет, может ли здание отдать ресурс

        Возвращает:
        bool - True если есть ресурсы для передачи, False если нет

        Логика:
        - Для производственных зданий: проверяет наличие output_resource
        - Для буров: проверяет наличие добытого ресурса
        - Для ядра: всегда True (бесконечное хранилище)
        """


class MineDrill(Building):
    """Базовый класс для буров (шахт)"""

    def __init__(self, scale: float, x: float, y: float, drill_type: str,
                 cell_resource: str, cost: ResourceCost, name: str, fuel_required: bool = False):
        """
        Инициализация бура

        Параметры:
        filename: str - путь к изображению (32x32 пикселей)
        scale: float - масштаб (0.5 для 16px)
        x: float - позиция X центра в пикселях
        y: float - позиция Y центра в пикселях
        drill_type: str - тип бура ('угольный' или 'электрический')
        cell_resource: str - ресурс клетки для добычи ('Медь', 'Уголь' и т.д.)
        cost: ResourceCost - стоимость постройки
        name: str - название здания
        fuel_required: bool = False - требуется ли топливо (уголь) для работы

        Атрибуты:
        self.drill_type: str - тип бура
        self.cell_resource: str - ресурс для добычи
        self.fuel_required: bool - потребляет ли топливо
        self.production_timer: float = 0.0 - таймер производства
        self.production_time: float - время добычи в секундах
        self.output_resource: str = cell_resource - что производит бур
        """
        # Определяем вместимость ресурсов
        resource_capacity = {"any": 1}  # Может хранить один любой ресурс
        if fuel_required:
            resource_capacity = {"Уголь": 1}  # Для угольного бура нужно топливо

        super().__init__('Изображения/Здания/Буры/Бур.png', scale, x, y, size=1,
                         resource_capacity=resource_capacity,
                         cost=cost, name=name)

        self.drill_type = drill_type
        self.cell_resource = cell_resource
        self.fuel_required = fuel_required
        self.output_resource = cell_resource  # Бур производит ресурс клетки

        # Время добычи зависит от типа бура
        self.production_time = 3.0 if drill_type == "угольный" else 1.0
        self.production_timer = 0.0

    def update(self, delta_time: float):
        pass
        """
        Обновление состояния бура

        Параметры:
        delta_time: float - время с предыдущего кадра в секундах

        Логика:
        - Увеличивает таймер производства
        - Если таймер >= production_time - пытается произвести ресурс
        - Для угольного бура проверяет наличие угля
        - При успехе добавляет ресурс cell_resource в здание
        - Сбрасывает таймер
        - Обрабатывает очереди дронов
        """

    def produce_resource(self):
        pass
        """
        Добывает ресурс с клетки

        Логика:
        - Для угольного бура: проверяет наличие угля, потребляет его, добывает ресурс
        - Для электрического бура: сразу добывает ресурс
        - Добавляет ресурс cell_resource во внутреннее хранилище
        - Если нет места - ресурс не добывается (теряется)
        - После производства вызывает can_give_resource() для проверки
        """

    def can_give_resource(self) -> bool:
        pass
        """
        Проверяет, может ли бур отдать ресурс

        Возвращает:
        bool - True если есть добытый ресурс, False если нет

        Логика:
        - Проверяет наличие cell_resource в ресурсах
        - Возвращает True если количество > 0
        """


class ElectricDrill(MineDrill):
    """Электрический бур - быстро добывает, ничего не потребляет"""

    def __init__(self, filename: str, scale: float, x: float, y: float, cell_resource: str):
        """
        Инициализация электрического бура

        Параметры:
        filename: str - путь к изображению
        scale: float - масштаб
        x: float - позиция X центра
        y: float - позиция Y центра
        cell_resource: str - ресурс клетки для добычи

        Атрибуты:
        self.hp: int = 5 - здоровье из констант
        self.max_hp: int = 5 - максимальное здоровье
        self.production_time: float = 1.0 - время добычи
        self.fuel_required: bool = False - не требует топлива
        self.output_resource: str = cell_resource - что производит
        """
        cost = ResourceCost([[3, 'Медь'], [1, 'Железо']])
        super().__init__(filename, scale, x, y,
                         drill_type="электрический",
                         cell_resource=cell_resource,
                         cost=cost,
                         name="Электрический бур",
                         fuel_required=False)

        self.hp = BUILDING_HP["Электрический бур"]
        self.max_hp = self.hp


class ProductionBuilding(Building):
    """Базовый класс для производственных зданий"""

    def __init__(self, filename: str, scale: float, x: float, y: float, size: int,
                 input_resources: Dict[str, int], output_resource: str,
                 production_time: float, cost: ResourceCost, name: str):
        """
        Инициализация производственного здания

        Параметры:
        filename: str - путь к изображению
        scale: float - масштаб
        x: float - позиция X центра
        y: float - позиция Y центра
        size: int - размер в клетках (2 или 3)
        input_resources: Dict[str, int] - входные ресурсы {'Медь': 1, 'Олово': 1}
        output_resource: str - выходной ресурс 'Бронза'
        production_time: float - время производства в секундах
        cost: ResourceCost - стоимость постройки
        name: str - название здания

        Атрибуты:
        self.input_resources: Dict[str, int] - рецепт производства
        self.output_resource: str - результат производства
        self.production_time: float - время цикла производства
        self.production_timer: float = 0.0 - текущий таймер
        self.can_produce: bool = False - флаг готовности к производству
        """
        # Создаем вместимость для всех ресурсов (входные + выходной)
        capacity = input_resources.copy()
        capacity[output_resource] = 1  # Может хранить свой выходной ресурс

        super().__init__(filename, scale, x, y, size=size,
                         resource_capacity=capacity,
                         cost=cost,
                         name=name)

        self.input_resources = input_resources
        self.output_resource = output_resource  # Устанавливаем выходной ресурс
        self.production_time = production_time
        self.production_timer = 0.0
        self.can_produce = False

    def update(self, delta_time: float):
        pass
        """
        Обновление состояния производства

        Параметры:
        delta_time: float - время с предыдущего кадра

        Логика:
        - Проверяет возможность производства (has_all_inputs())
        - Если можно производить - увеличивает таймер
        - При достижении production_time - производит ресурс
        - Сбрасывает таймер после производства
        - Обрабатывает очереди дронов
        """

    def has_all_inputs(self) -> bool:
        pass
        """
        Проверяет наличие всех необходимых ресурсов для производства

        Возвращает:
        bool - True если все ресурсы есть, False если чего-то не хватает

        Логика:
        - Проверяет наличие каждого входного ресурса
        - Для каждого ресурса проверяет количество
        - Возвращает False при первой нехватке
        """

    def produce_output(self):
        pass
        """
        Производит выходной ресурс

        Логика:
        - Проверяет has_all_inputs() еще раз
        - Тратит все входные ресурсы
        - Добавляет выходной ресурс во внутреннее хранилище
        - Сбрасывает таймер производства
        """

    def can_give_resource(self) -> bool:
        pass
        """
        Проверяет, может ли здание отдать ресурс

        Возвращает:
        bool - True если есть выходной ресурс, False если нет

        Логика:
        - Проверяет наличие output_resource в ресурсах
        - Возвращает True если количество > 0
        """


class BronzeFurnace(ProductionBuilding):
    """Печь для бронзы - производит бронзу из меди, олова и угля"""

    def __init__(self, scale: float, x: float, y: float):
        """
        Инициализация печи для бронзы

        Параметры:
        filename: str - путь к изображению
        scale: float - масштаб
        x: float - позиция X центра
        y: float - позиция Y центра

        Атрибуты:
        self.size: int = 2 - размер 2x2 клетки
        self.hp: int = 5 - здоровье из констант
        self.max_hp: int = 5 - максимальное здоровье
        self.input_resources: Dict[str, int] = {'Медь': 1, 'Олово': 1, 'Уголь': 1}
        self.output_resource: str = 'Бронза'
        self.production_time: float = 2.0 - время производства в секундах
        """
        cost = ResourceCost([[3, 'Медь'], [1, 'Олово']])
        super().__init__('Изображения/Здания/Заводы/Печь.png', scale, x, y, size=2,
                         input_resources={"Медь": 1, "Олово": 1, "Уголь": 1},
                         output_resource="Бронза",
                         production_time=2.0,
                         cost=cost,
                         name="Печь для бронзы")

        self.hp = BUILDING_HP["Печь для бронзы"]
        self.max_hp = self.hp


class SiliconFurnace(ProductionBuilding):
    """Кремниевая печь - производит кремний из песка и угля"""

    def __init__(self, scale: float, x: float, y: float):
        """
        Инициализация кремниевой печи

        Параметры:
        filename: str - путь к изображению
        scale: float - масштаб
        x: float - позиция X центра
        y: float - позиция Y центра

        Атрибуты:
        self.size: int = 2 - размер 2x2 клетки
        self.hp: int = 5 - здоровье из констант
        self.max_hp: int = 5 - максимальное здоровье
        self.input_resources: Dict[str, int] = {'Песок': 1, 'Уголь': 1}
        self.output_resource: str = 'Кремний'
        self.production_time: float = 2.0 - время производства в секундах
        """
        cost = ResourceCost([[2, 'Медь'], [1, 'Песок']])
        super().__init__('Изображения/Здания/Заводы/Печь.png', scale, x, y, size=2,
                         input_resources={"Песок": 1, "Уголь": 1},
                         output_resource="Кремний",
                         production_time=2.0,
                         cost=cost,
                         name="Кремниевая печь")

        self.hp = BUILDING_HP["Кремниевая печь"]
        self.max_hp = self.hp


class AmmoFactory(ProductionBuilding):
    """Завод боеприпасов - производит боеприпасы из олова и угля"""

    def __init__(self, scale: float, x: float, y: float):
        """
        Инициализация завода боеприпасов

        Параметры:
        filename: str - путь к изображению
        scale: float - масштаб
        x: float - позиция X центра
        y: float - позиция Y центра

        Атрибуты:
        self.size: int = 2 - размер 2x2 клетки
        self.hp: int = 5 - здоровье из констант
        self.max_hp: int = 5 - максимальное здоровье
        self.input_resources: Dict[str, int] = {'Олово': 1, 'Уголь': 1}
        self.output_resource: str = 'Боеприпасы'
        self.production_time: float = 1.0 - время производства в секундах
        """
        cost = ResourceCost([[2, 'Медь'], [1, 'Олово']])
        super().__init__('Изображения/Здания/Заводы/Завод.png', scale, x, y, size=2,
                         input_resources={"Олово": 1, "Уголь": 1},
                         output_resource="Боеприпасы",
                         production_time=1.0,
                         cost=cost,
                         name="Завод боеприпасов")

        self.hp = BUILDING_HP["Завод боеприпасов"]
        self.max_hp = self.hp


class Turret(Building):
    """Базовый класс для турелей"""

    def __init__(self, scale: float,
                 x: float, y: float, size: int, damage: int, range_seconds: float,
                 cooldown: float, ammo_requirements: Dict[str, int], name: str):
        """
        Инициализация турели

        Параметры:
        base_filename: str - путь к изображению основы (32x32 пикселей)
        tower_filename: str - путь к изображению башни (32x32 пикселей)
        scale: float - масштаб (0.5 для 16px)
        x: float - позиция X центра турели
        y: float - позиция Y центра турели
        size: int - размер в клетках (2)
        damage: int - урон по врагам
        range_seconds: float - дальность стрельбы (время жизни пули в секундах)
        cooldown: float - время перезарядки в секундах
        ammo_requirements: Dict[str, int] - боеприпасы {'Медь': 1}
        name: str - название турели

        Атрибуты:
        self.base_sprite: arcade.Sprite - неподвижная основа
        self.tower_sprite: arcade.Sprite - подвижная башня
        self.bullet_list: arcade.SpriteList - список пуль турели
        self.current_cooldown: float = 0.0 - текущий таймер перезарядки
        self.target: Any = None - текущая цель
        self.tower_angle: float = 0.0 - угол поворота башни
        """
        # Вместимость для боеприпасов
        capacity = ammo_requirements.copy()

        super().__init__('Изображения/Здания/Турели/РГ турель основание.png',
                         resource_capacity=capacity,
                         cost=ResourceCost([[1, 'Медь']]),  # базовая стоимость
                         name=name)

        # Неподвижная основа
        self.base_sprite = arcade.Sprite('Изображения/Здания/Турели/РГ турель основание.png', scale)
        self.base_sprite.center_x = x
        self.base_sprite.center_y = y

        # Подвижная башня
        self.tower_sprite = arcade.Sprite('Изображения/Здания/Турели/РГ турель башня.png', scale)
        self.tower_sprite.center_x = x
        self.tower_sprite.center_y = y
        self.tower_angle = 0.0

        # Параметры стрельбы
        self.damage = damage
        self.range_seconds = range_seconds
        self.max_cooldown = cooldown
        self.current_cooldown = 0.0
        self.ammo_requirements = ammo_requirements
        self.bullet_list = arcade.SpriteList()
        self.target = None

    def update(self, delta_time: float):
        pass
        """
        Обновление состояния турели

        Параметры:
        delta_time: float - время с предыдущего кадра

        Логика:
        - Уменьшает таймер перезарядки
        - Если перезарядка готова и есть боеприпасы - ищет цель
        - Если есть цель - поворачивает башню и стреляет
        - Обновляет все пули в bullet_list
        - Обрабатывает очереди дронов
        """

    def has_ammo(self) -> bool:
        pass
        """
        Проверяет наличие боеприпасов

        Возвращает:
        bool - True если есть все необходимые боеприпасы, False если чего-то не хватает

        Логика:
        - Проверяет наличие каждого типа боеприпасов
        - Возвращает False при первой нехватке
        """

    def find_target(self):
        pass
        """
        Ищет ближайшую цель для атаки

        Логика:
        - Сначала проверяет игрока (если ближе всех)
        - Затем ищет ближайшего жука в пределах дальности
        - Вычисляет расстояние до каждой цели
        - Выбирает самую близкую
        - Если целей нет - self.target = None
        """

    def shoot(self):
        pass
        """
        Производит выстрел

        Логика:
        - Тратит боеприпасы
        - Создает пулю в направлении цели
        - Устанавливает таймер перезарядки
        - Добавляет пулю в bullet_list и общий список пуль игры
        """

    def can_give_resource(self) -> bool:
        pass
        """
        Проверяет, может ли турель отдать ресурс

        Возвращает:
        bool - False

        Логика:
        - Турели никогда не отдают ресурсы
        - Только потребляют боеприпасы
        """


class CopperTurret(Turret):
    """Медная турель - базовая турель, стреляет медью"""

    def __init__(self, base_filename: str, tower_filename: str, scale: float, x: float, y: float):
        """
        Инициализация медной турели

        Параметры:
        base_filename: str - путь к изображению основы
        tower_filename: str - путь к изображению башни
        scale: float - масштаб
        x: float - позиция X центра
        y: float - позиция Y центра

        Атрибуты:
        self.size: int = 2 - размер 2x2 клетки
        self.hp: int = 5 - здоровье из констант
        self.max_hp: int = 5 - максимальное здоровье
        self.damage: int = 1 - урон по врагам
        self.range_seconds: float = 3.0 - дальность стрельбы
        self.max_cooldown: float = 1.0 - время перезарядки в секундах
        self.ammo_requirements: Dict[str, int] = {'Медь': 1} - боеприпасы
        """
        cost = ResourceCost([[2, 'Медь']])
        super().__init__(base_filename, tower_filename, scale, x, y, size=2,
                         damage=1,
                         range_seconds=3.0,
                         cooldown=1.0,
                         ammo_requirements={"Медь": 1},
                         name="Медная турель",
                         cost=cost)

        self.hp = BUILDING_HP["Медная турель"]
        self.max_hp = self.hp


class BronzeTurret(Turret):
    """Бронзовая турель - средняя турель, стреляет боеприпасами"""

    def __init__(self, base_filename: str, tower_filename: str, scale: float, x: float, y: float):
        """
        Инициализация бронзовой турели

        Параметры:
        base_filename: str - путь к изображению основы
        tower_filename: str - путь к изображению башни
        scale: float - масштаб
        x: float - позиция X центра
        y: float - позиция Y центра

        Атрибуты:
        self.size: int = 2 - размер 2x2 клетки
        self.hp: int = 10 - здоровье из констант
        self.max_hp: int = 10 - максимальное здоровье
        self.damage: int = 2 - урон по врагам
        self.range_seconds: float = 4.0 - дальность стрельбы
        self.max_cooldown: float = 1.0 - время перезарядки в секундах
        self.ammo_requirements: Dict[str, int] = {'Боеприпасы': 1} - боеприпасы
        """
        cost = ResourceCost([[3, 'Медь'], [2, 'Бронза']])
        super().__init__(base_filename, tower_filename, scale, x, y, size=2,
                         damage=2,
                         range_seconds=4.0,
                         cooldown=1.0,
                         ammo_requirements={"Боеприпасы": 1},
                         name="Бронзовая турель",
                         cost=cost)

        self.hp = BUILDING_HP["Бронзовая турель"]
        self.max_hp = self.hp


class LongRangeTurret(Turret):
    """Дальняя турель - мощная турель, стреляет боеприпасами и микросхемами"""

    def __init__(self, base_filename: str, tower_filename: str, scale: float, x: float, y: float):
        """
        Инициализация дальней турели

        Параметры:
        base_filename: str - путь к изображению основы
        tower_filename: str - путь к изображению башни
        scale: float - масштаб
        x: float - позиция X центра
        y: float - позиция Y центра

        Атрибуты:
        self.size: int = 2 - размер 2x2 клетки
        self.hp: int = 5 - здоровье из констант
        self.max_hp: int = 5 - максимальное здоровье
        self.damage: int = 6 - урон по врагам
        self.range_seconds: float = 5.0 - дальность стрельбы
        self.max_cooldown: float = 2.0 - время перезарядки в секундах
        self.ammo_requirements: Dict[str, int] = {'Боеприпасы': 1, 'Микросхема': 1} - боеприпасы
        """
        cost = ResourceCost([[4, 'Медь'], [3, 'Бронза'], [2, 'Микросхема']])
        super().__init__(base_filename, tower_filename, scale, x, y, size=2,
                         damage=6,
                         range_seconds=5.0,
                         cooldown=2.0,
                         ammo_requirements={"Боеприпасы": 1, "Микросхема": 1},
                         name="Дальняя турель",
                         cost=cost)

        self.hp = BUILDING_HP["Дальняя турель"]
        self.max_hp = self.hp


class Drone(arcade.Sprite):
    """Дрон для доставки ресурсов - ключевой элемент логистики"""

    def __init__(self, scale: float, route: [Building, Building], core: 'Core'):
        """
        Инициализация дрона

        Параметры:
        filename: str - путь к изображению дрона (32x32 пикселей)
        scale: float - масштаб (0.5 для 16px)
        station: DroneStation - станция-владелец

        Атрибуты:
        self.station: DroneStation - ссылка на станцию
        self.cargo: Optional[str] = None - текущий ресурс в грузе
        self.source: Optional[Building] = None - здание-источник для забора
        self.destination: Optional[Building] = None - здание-приемник для доставки
        self.path: List[Tuple[float, float]] = [] - путь следования
        self.current_waypoint: int = 0 - текущая точка пути
        self.state: str = "WAITING_AT_STATION" - состояние дрона:
            - WAITING_AT_STATION: ждет на станции
            - FLYING_TO_SOURCE: летит к источнику
            - WAITING_AT_SOURCE: ждет в очереди у источника
            - TAKING_RESOURCE: получает ресурс от источника
            - FLYING_TO_DEST: летит к приемнику
            - WAITING_AT_DEST: ждет в очереди у приемника
            - GIVING_RESOURCE: отдает ресурс приемнику
            - RETURNING_TO_STATION: возвращается на станцию
        self.hp: int = 2 - здоровье дрона
        self.max_hp: int = 2 - максимальное здоровье
        self.speed: float = 16.0 - скорость в пикселях/сек (1 блок/сек)
        """
        super().__init__('Изображения/Остальное/Дрон.png', scale)
        self.core = core
        self.cargo = None
        self.source = None  # Здание-источник
        self.destination = None  # Здание-приемник
        self.path = []
        self.current_waypoint = 0
        self.state = "WAITING_AT_STATION"  # Начинает над станцией
        self.hp = 2
        self.max_hp = 2
        self.speed = 16.0  # 1 блок/сек = 16 пикселей/сек

        # Начальная позиция - над станцией
        self.center_x = core.center_x
        self.center_y = core.center_y + 32

    def set_route(self, source: Building, destination: Building):
        pass
        """
        Устанавливает маршрут от источника к приемнику

        Параметры:
        source: Building - здание-источник
        destination: Building - здание-приемник

        Логика:
        - Сохраняет источник и приемник
        - Устанавливает состояние FLYING_TO_SOURCE
        - Вычисляет путь к источнику
        - Добавляет себя в очередь источника
        """

    def calculate_path_to_source(self):
        pass
        """
        Вычисляет путь к источнику ресурсов

        Логика:
        - Путь всегда кратчайший: сначала по X до source.center_x, потом по Y до source.center_y
        - Создает список точек с шагом self.speed
        - Не обходит препятствия (летит напролом)
        """

    def calculate_path_to_destination(self):
        pass
        """
        Вычисляет путь к приемнику ресурсов

        Логика:
        - Аналогична calculate_path_to_source()
        - Создает путь от текущей позиции до приемника
        - Не обходит препятствия
        """

    def calculate_path_to_station(self):
        pass
        """
        Вычисляет путь обратно к станции

        Логика:
        - Создает путь от текущей позиции до станции
        - Кратчайший путь: сначала по X, потом по Y
        """

    def update(self, delta_time: float):
        pass
        """
        Основной цикл дрона

        Параметры:
        delta_time: float - время с предыдущего кадра

        Логика для каждого состояния:
        1. WAITING_AT_STATION:
           - Ждет на станции
           - Если станция установила маршрут - переходит в FLYING_TO_SOURCE
           - Если станция уничтожена - дрон уничтожается

        2. FLYING_TO_SOURCE:
           - Движется к источнику по пути
           - При достижении источника - добавляет себя в waiting_drones
           - Переходит в WAITING_AT_SOURCE

        3. WAITING_AT_SOURCE:
           - Ждет в очереди источника
           - Когда доходит очередь - проверяет расстояние
           - Если на расстоянии DRONE_PICKUP_DISTANCE - переходит в TAKING_RESOURCE
           - Если источник уничтожен - возвращается на станцию

        4. TAKING_RESOURCE:
           - Получает ресурс от источника
           - Если успешно получил - выходит из очереди и переходит в FLYING_TO_DEST
           - Если неуспешно - остается в состоянии

        5. FLYING_TO_DEST:
           - Движется к приемнику по пути
           - При достижении приемника - добавляет себя в waiting_for_unload
           - Переходит в WAITING_AT_DEST

        6. WAITING_AT_DEST:
           - Ждет в очереди приемника
           - Когда доходит очередь - проверяет расстояние
           - Если на расстоянии DRONE_DROP_DISTANCE - переходит в GIVING_RESOURCE
           - Если приемник уничтожен - возвращается на станцию

        7. GIVING_RESOURCE:
           - Отдает ресурс приемнику
           - Если успешно отдал - выходит из очереди и переходит в RETURNING_TO_STATION
           - Если неуспешно - остается в состоянии

        8. RETURNING_TO_STATION:
           - Движется обратно к станции
           - При достижении станции - переходит в WAITING_AT_STATION

        Особенности:
        - Если станция уничтожена - дрон уничтожается
        - Если здание в очереди уничтожено - удаляется из всех очередей и возвращается на станцию
        - При уничтожении дрона - вызывает recover_drone() у станции
        """

    def move_along_path(self, delta_time: float):
        pass
        """
        Движение по пути к следующей точке

        Параметры:
        delta_time: float - время с предыдущего кадра

        Логика:
        - Если есть следующая точка в пути - двигается к ней
        - Вычисляет вектор движения
        - Двигается с постоянной скоростью
        - При достижении точки переходит к следующей
        """

    def distance_to(self, target: arcade.Sprite) -> float:
        pass
        """
        Вычисляет расстояние до цели

        Параметры:
        target: arcade.Sprite - цель для измерения расстояния

        Возвращает:
        float - расстояние в пикселях между центрами спрайтов
        """

    def reached_waypoint(self) -> bool:
        pass
        """
        Проверяет, достиг ли дрон текущей точки пути

        Возвращает:
        bool - True если достиг текущей точки, False если нет

        Логика:
        - Сравнивает текущую позицию с целевой точкой
        - Если расстояние < 5 пикселей - считается достигшим
        """

    def take_damage(self, amount: int):
        pass
        """
        Получает урон дроном

        Параметры:
        amount: int - количество урона

        Логика:
        - Уменьшает HP на amount
        - Если HP <= 0 - дрон уничтожен
        - При уничтожении дрона:
          * Если станция жива - вызывает station.recover_drone()
          * Если станция уничтожена - дрон исчезает без восстановления
        - Не позволяет HP быть меньше 0
        """

    def remove_from_queues(self):
        pass
        """
        Удаляет дрона из всех очередей

        Логика:
        - Если есть source - удаляет из waiting_drones источника
        - Если есть destination - удаляет из waiting_for_unload приемника
        - Если есть станция - удаляет из всех связанных очередей
        """

    def handle_building_destroyed(self, building: Building):
        pass
        """
        Обрабатывает разрушение здания

        Параметры:
        building: Building - уничтоженное здание

        Логика:
        - Если разрушен источник:
          * Если дрон в состояниях WAITING_AT_SOURCE/TAKING_RESOURCE - переходит в RETURNING_TO_STATION
          * Удаляет себя из очереди источника
          * Ресурс, если был в грузе, исчезает
        - Если разрушен приемник:
          * Если дрон в состояниях WAITING_AT_DEST/GIVING_RESOURCE - переходит в RETURNING_TO_STATION
          * Удаляет себя из очереди приемника
          * Ресурс в грузе исчезает
        - Если разрушена станция - дрон уничтожается
        """
# buildings.py
import arcade
from typing import Dict, Optional, Deque
from collections import deque
import random, math

from constants import *
from resources import ResourceTransaction, ResourceStorage
from sprite_list import good_bullet, bugs
from enemies import Bug

# Константы здоровья (из constants.py)
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


# =========== БАЗОВЫЙ КЛАСС Building ===========
class Building(arcade.Sprite):
    """Базовый класс для всех зданий"""

    def __init__(
            self,
            image_path: str,
            scale: float,
            x: float,
            y: float,
            name: str,
            hp: int,
            cost: ResourceTransaction,
            storage_capacity: Dict[str, int] = None,
            size: int = 1
    ):
        super().__init__(image_path, scale)

        # Основные свойства
        self.center_x = x
        self.center_y = y
        self.name = name

        # Здоровье
        self.hp = hp
        self.max_hp = hp
        self.is_destroyed = False

        # Ресурсы
        self.cost = cost
        self.storage = ResourceStorage(storage_capacity)

        # Для производства
        self.production_timer = 0.0
        self.production_time = 0.0  # 0 = не производит

        # Для дронов (очень просто)
        self.waiting_drones = deque()  # Дроны ждут загрузки
        self.waiting_unload = deque()  # Дроны ждут разгрузки
        self.attached_drones = set()  # Дроны, привязанные к этому зданию

    # === 3 МЕТОДА ДЛЯ ОБЩЕГО ДОСТУПА ===

    def take_damage(self, amount: int) -> bool:
        """Получить урон, возвращает True если уничтожено"""
        if self.is_destroyed:
            return True

        self.hp = max(0, self.hp - amount)
        if self.hp <= 0:
            self._destroy()
            return True
        return False

    def demolish(self) -> ResourceTransaction:
        """Игрок сносит здание, возвращает 50% ресурсов"""
        refund = self.cost.get_refund(0.5)
        self._destroy()
        return refund

    def update(self, delta_time: float):
        """Обновление каждый кадр - здание работает автономно"""
        if self.is_destroyed:
            return

        # 1. Производство
        self._update_production(delta_time)

        # 2. Обслуживание дронов
        self._process_drones()

    # === ВНУТРЕННИЕ МЕТОДЫ ===

    def _update_production(self, delta_time: float):
        """Внутренняя логика производства"""
        if self.production_time <= 0:
            return

        self.production_timer += delta_time
        if self.production_timer >= self.production_time:
            self._produce()
            self.production_timer = 0.0

    def _produce(self):
        """Один цикл производства - переопределяется"""
        pass

    def _process_drones(self):
        """Обслуживание очередей дронов"""
        # Сначала разгружаем
        while self.waiting_unload:
            drone = self.waiting_unload[0]
            if self._unload_drone(drone):
                self.waiting_unload.popleft()
            else:
                break

        # Потом загружаем
        while self.waiting_drones:
            drone = self.waiting_drones[0]
            if self._load_drone(drone):
                self.waiting_drones.popleft()
            else:
                break

    def _unload_drone(self, drone) -> bool:
        """Разгрузить дрона"""
        if not drone.is_close_to(self):
            return False

        cargo = drone.get_cargo()
        if not cargo:
            return False

        if self.storage.can_add(cargo, 1) and self.storage.add(cargo, 1):
            drone.unload()
            return True
        return False

    def _load_drone(self, drone) -> bool:
        """Загрузить дрона"""
        if not drone.is_close_to(self):
            return False

        # Какой ресурс нужен дрону?
        needed = drone.get_needed_resource()
        if not needed:
            # Берём первый доступный
            for res, amt in self.storage.get_all().items():
                if amt > 0:
                    needed = res
                    break
            if not needed:
                return False

        if self.storage.has(needed, 1) and self.storage.remove(needed, 1):
            drone.load(needed)
            return True
        return False

    def _destroy(self):
        """Полное уничтожение здания"""
        self.is_destroyed = True
        self.storage.clear()

        # Оповещаем дронов
        for drone in list(self.attached_drones):
            drone.on_building_destroyed(self)
        self.attached_drones.clear()

        # Очищаем очереди
        self.waiting_drones.clear()
        self.waiting_unload.clear()

    # === ПУБЛИЧНЫЕ МЕТОДЫ ===

    def can_accept(self, resource: str) -> bool:
        """Может ли принять ресурс?"""
        return self.storage.can_add(resource, 1)

    def has_resource(self, resource: str = None) -> bool:
        """Есть ли ресурс?"""
        if resource:
            return self.storage.has(resource, 1)
        return not self.storage.is_empty()

    def attach_drone(self, drone):
        """Привязать дрона"""
        self.attached_drones.add(drone)

    def detach_drone(self, drone):
        """Отвязать дрона"""
        self.attached_drones.discard(drone)

    def drone_wants_unload(self, drone):
        """Дрон хочет разгрузиться"""
        self.waiting_unload.append(drone)

    def drone_wants_load(self, drone):
        """Дрон хочет загрузиться"""
        self.waiting_drones.append(drone)

    def get_info(self) -> Dict:
        """Информация для UI"""
        return {
            "name": self.name,
            "hp": f"{self.hp}/{self.max_hp}",
            "resources": str(self.storage),
            "production": f"{self.production_timer:.1f}/{self.production_time}s"
            if self.production_time > 0 else "Нет"
        }


# =========== КОНКРЕТНЫЕ ЗДАНИЯ ===========

# ----------- БУРЫ -----------
class MineDrill(Building):
    """Базовый класс для буров"""

    def __init__(
            self,
            image_path: str,
            scale: float,
            x: float, y: float,
            drill_type: str,
            resource_type: str,
            cost: ResourceTransaction,
            name: str,
            needs_coal: bool = False
    ):
        # Вместимость зависит от типа
        capacity = {resource_type: 10}  # Может хранить 10 добытого ресурса
        if needs_coal:
            capacity["Уголь"] = 5  # Угольный бур хранит уголь для работы

        super().__init__(
            image_path=image_path,
            scale=scale,
            x=x, y=y,
            name=name,
            hp=BUILDING_HP.get(name, 5),
            cost=cost,
            storage_capacity=capacity,
            size=1
        )

        self.drill_type = drill_type
        self.resource_type = resource_type
        self.needs_coal = needs_coal

        # Время добычи
        if drill_type == "угольный":
            self.production_time = 3.0
        else:  # электрический
            self.production_time = 1.0

    def _produce(self):
        """Добывает ресурс"""
        if self.needs_coal:
            # Проверяем есть ли уголь
            if not self.storage.has("Уголь", 1):
                return
            # Тратим уголь
            self.storage.remove("Уголь", 1)

        # Добываем ресурс
        self.storage.add(self.resource_type, 1)


class CoalDrill(MineDrill):
    """Угольный бур - медленный, требует уголь"""

    def __init__(self, x: float, y: float, resource_type: str = "Медь"):
        cost = ResourceTransaction({"Медь": 2})
        super().__init__(
            image_path="Изображения/Здания/Буры/Бур.png",
            scale=0.25,
            x=x, y=y,
            drill_type="угольный",
            resource_type=resource_type,
            cost=cost,
            name="Угольный бур",
            needs_coal=True
        )


class ElectricDrill(MineDrill):
    """Электрический бур - быстрый, не требует топлива"""

    def __init__(self, x: float, y: float, resource_type: str = "Медь"):
        cost = ResourceTransaction({"Медь": 3, "Железо": 1})
        super().__init__(
            image_path="Изображения/Здания/Буры/Бур.png",
            scale=0.25,
            x=x, y=y,
            drill_type="электрический",
            resource_type=resource_type,
            cost=cost,
            name="Электрический бур",
            needs_coal=False
        )
        self.hp = BUILDING_HP["Электрический бур"]
        self.max_hp = self.hp


# ----------- ПРОИЗВОДСТВЕННЫЕ ЗДАНИЯ -----------
class ProductionBuilding(Building):
    """Базовый класс для производств"""

    def __init__(
            self,
            image_path: str,
            scale: float,
            x: float, y: float,
            size: int,
            recipe: Dict[str, int],  # Что нужно {"Медь": 1, "Олово": 1}
            output: str,  # Что получается "Бронза"
            production_time: float,
            cost: ResourceTransaction,
            name: str
    ):
        # Вместимость = входные ресурсы + выход
        capacity = recipe.copy()
        capacity[output] = 10  # Может хранить 10 выходного ресурса

        super().__init__(
            image_path=image_path,
            scale=scale,
            x=x, y=y,
            name=name,
            hp=BUILDING_HP.get(name, 5),
            cost=cost,
            storage_capacity=capacity,
            size=size
        )

        self.recipe = recipe
        self.output = output
        self.production_time = production_time

    def _produce(self):
        """Производит выходной ресурс"""
        # 1. Проверяем все ли ингредиенты есть
        for ingredient, amount in self.recipe.items():
            if not self.storage.has(ingredient, amount):
                return  # Не хватает чего-то

        # 2. Проверяем есть ли место для продукта
        if not self.storage.can_add(self.output, 1):
            return  # Нет места

        # 3. Забираем ингредиенты
        for ingredient, amount in self.recipe.items():
            self.storage.remove(ingredient, amount)

        # 4. Добавляем продукт
        self.storage.add(self.output, 1)


class BronzeFurnace(ProductionBuilding):
    """Печь для бронзы"""

    def __init__(self, x: float, y: float):
        cost = ResourceTransaction({"Медь": 3, "Олово": 1})
        super().__init__(
            image_path="Изображения/Здания/Заводы/Печь.png",
            scale=0.25,
            x=x, y=y,
            size=2,
            recipe={"Медь": 1, "Олово": 1, "Уголь": 1},
            output="Бронза",
            production_time=2.0,
            cost=cost,
            name="Печь для бронзы"
        )
        self.hp = BUILDING_HP["Печь для бронзы"]
        self.max_hp = self.hp


class SiliconFurnace(ProductionBuilding):
    """Кремниевая печь"""

    def __init__(self, x: float, y: float):
        cost = ResourceTransaction({"Медь": 2, "Песок": 1})
        super().__init__(
            image_path="Изображения/Здания/Заводы/Печь.png",
            scale=0.25,
            x=x, y=y,
            size=2,
            recipe={"Песок": 1, "Уголь": 1},
            output="Кремний",
            production_time=2.0,
            cost=cost,
            name="Кремниевая печь"
        )
        self.hp = BUILDING_HP["Кремниевая печь"]
        self.max_hp = self.hp


class AmmoFactory(ProductionBuilding):
    """Завод боеприпасов"""

    def __init__(self, x: float, y: float):
        cost = ResourceTransaction({"Медь": 2, "Олово": 1})
        super().__init__(
            image_path="Изображения/Здания/Заводы/Завод.png",
            scale=0.25,
            x=x, y=y,
            size=2,
            recipe={"Олово": 1, "Уголь": 1},
            output="Боеприпасы",
            production_time=1.0,
            cost=cost,
            name="Завод боеприпасов"
        )
        self.hp = BUILDING_HP["Завод боеприпасов"]
        self.max_hp = self.hp


# ----------- ТУРЕЛИ -----------
class Turret(Building):
    """Базовый класс для турелей"""

    def __init__(
            self,
            base_image: str,
            tower_image: str,
            scale: float,
            x: float, y: float,
            size: int,
            damage: int,
            attack_range: float,  # в пикселях
            bullet_lifetime: float,
            bullet_speed: float,
            cooldown: float,
            ammo_type: str,  # Тип боеприпасов
            ammo_per_shot: int,  # Сколько тратит за выстрел
            cost: ResourceTransaction,
            name: str
    ):
        # Турель хранит только боеприпасы
        capacity = {ammo_type: 50}  # До 50 патронов

        super().__init__(
            image_path=base_image,
            scale=scale,
            x=x, y=y,
            name=name,
            hp=BUILDING_HP.get(name, 5),
            cost=cost,
            storage_capacity=capacity,
            size=size
        )

        # Дополнительные спрайты
        self.base_sprite = arcade.Sprite(base_image, scale)
        self.base_sprite.center_x = x
        self.base_sprite.center_y = y

        self.tower_sprite = arcade.Sprite(tower_image, scale)
        self.tower_sprite.center_x = x
        self.tower_sprite.center_y = y
        self.tower_angle = 0.0

        # Параметры стрельбы
        self.damage = damage
        self.attack_range = attack_range
        self.bullet_lifetime = bullet_lifetime
        self.bullet_speed = bullet_speed
        self.cooldown_time = cooldown
        self.current_cooldown = 0.0
        self.ammo_type = ammo_type
        self.ammo_per_shot = ammo_per_shot

        # Для поиска цели
        self.target = None

        # self.bullets = arcade.SpriteList()  # Пули этой турели

    def update(self, delta_time: float):
        """Переопределяем для стрельбы"""
        super().update(delta_time)  # Базовая логика (дроны и т.д.)

        if self.is_destroyed:
            return

        # Обновляем перезарядку
        if self.current_cooldown > 0:
            self.current_cooldown -= delta_time

        # Обновляем пули
        # self.bullets.update() # update в игре через единый список для всех пуль

        # Если перезарядились и есть патроны - ищем цель
        if self.current_cooldown <= 0 and self.storage.has(self.ammo_type, self.ammo_per_shot):
            if self._find_target():
                self._shoot()

    def _find_target(self) -> bool:
        """
        Ищет цель в радиусе
        передавать список врагов через метод set_enemies()
        """
        self.set_enemies()
        if not self.potential_enemies:
            return False
        m = self.potential_enemies[0]
        ml = self.calculate_range(m.center_x, m.center_y)
        for enem in self.potential_enemies[1:]:
            if self.calculate_range(enem.center_x, enem.center_y) < ml:
                m = enem
                ml = enem.calculate_range(m.center_x, m.center_y)
        self.target = m
        return True

    def _shoot(self):
        """Производит выстрел"""
        # Тратим патроны
        if not self.storage.remove(self.ammo_type, self.ammo_per_shot):
            return

        self.current_cooldown = self.cooldown_time

        good_bullet.append(Shot_Bullet(self, target=self.target))

    def set_enemies(self, enemies_list = bugs):
        """для поиска цели"""
        self.potential_enemies = []
        for bug in enemies_list:
            if self.calculate_range(bug.center_x, bug.center_y) < 1 :
                self.potential_enemies.append(bug)

    def calculate_range(self, x, y) -> float:
        return (x ** 2 + y ** 2) / self.radius ** 2


class CopperTurret(Turret):
    """Медная турель"""

    def __init__(self, x: float, y: float):
        cost = ResourceTransaction({"Медь": 2})
        super().__init__(
            base_image="Изображения/Здания/Турели/РГ турель основание.png",
            tower_image="Изображения/Здания/Турели/РГ турель башня.png",
            scale=0.25,
            x=x, y=y,
            size=2,
            damage=1,
            attack_range=200,
            bullet_lifetime=3.0,
            bullet_speed=75.0,
            cooldown=1.0,
            ammo_type="Медь",
            ammo_per_shot=1,
            cost=cost,
            name="Медная турель"
        )
        self.hp = BUILDING_HP["Медная турель"]
        self.max_hp = self.hp


class BronzeTurret(Turret):
    """Бронзовая турель"""

    def __init__(self, x: float, y: float):
        cost = ResourceTransaction({"Медь": 3, "Бронза": 2})
        super().__init__(
            base_image="Изображения/Здания/Турели/РГ турель основание.png",
            tower_image="Изображения/Здания/Турели/РГ турель башня.png",
            scale=0.25,
            x=x, y=y,
            size=2,
            damage=2,
            attack_range=250,
            bullet_lifetime=3.5,
            bullet_speed=87.5,
            cooldown=0.7,
            ammo_type="Боеприпасы",
            ammo_per_shot=1,
            cost=cost,
            name="Бронзовая турель"
        )
        self.hp = BUILDING_HP["Бронзовая турель"]
        self.max_hp = self.hp


class LongRangeTurret(Turret):
    """Дальняя турель"""

    def __init__(self, x: float, y: float):
        cost = ResourceTransaction({"Медь": 4, "Бронза": 3, "Микросхема": 2})
        super().__init__(
            base_image="Изображения/Здания/Турели/РГ турель основание.png",
            tower_image="Изображения/Здания/Турели/РГ турель башня.png",
            scale=0.25,
            x=x, y=y,
            size=2,
            damage=6,
            attack_range=400,
            bullet_lifetime=4.0,
            bullet_speed=100.0,
            cooldown=2.0,
            ammo_type="Боеприпасы",
            ammo_per_shot=1,
            cost=cost,
            name="Дальняя турель"
        )
        # Дальняя турель требует и микросхемы тоже
        # self.storage.capacity["Микросхема"] = 20
        # self.storage.resources["Микросхема"] = 0

        self.hp = BUILDING_HP["Дальняя турель"]
        self.max_hp = self.hp


class Shot_Bullet(arcade.Sprite):
    """временный класс для выстрелов"""
    def __init__(self, source: 'Turret', target: 'Bug'):
        super().__init__('Изображения/Остальное/Пуля.png', 0.05)
        self.center_x = source.center_x
        self.center_y = source.center_y
        self.lifetime = source.bullet_lifetime
        self.damage = source.damage
        self.bullet_speed = source.bullet_speed
        self.attack_range = source.attack_range
        self.target = target
        self.velocity = (0.0, 0.0)
        self.set_velocity()

    def set_velocity(self):
        """устанавливает вектор движения пули"""
        x, y = self.target.center_x - self.source.center, self.target.center_y - self.source.center_y
        s = x + y
        self.velocity = (x / s, y / s)

    def update(self, delta_time: float):
        """двигаем пулю к цели"""
        self.lifetime -= delta_time
        if self.lifetime <= 0:
            self.remove_from_sprite_lists()

        self.center_x += int(self.velocity[0] * delta_time)
        self.center_y += int(self.velocity[1] * delta_time)


class Drone(arcade.Sprite):
    """Дрон для доставки ресурсов - ключевой элемент логистики"""

    def __init__(self, filename: str, scale: float, route: [Building, Building], core: 'Core'):
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
        super().__init__(filename, scale)
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
        self.source = source
        self.destination = destination
        self.state = "FLYING_TO_SOURCE"
        self.calculate_path_to_source()

    def calculate_path_to_source(self):
        """
        Вычисляет путь к источнику ресурсов

        Логика:
        - Путь всегда кратчайший: сначала по X до source.center_x, потом по Y до source.center_y
        - Создает список точек с шагом self.speed
        - Не обходит препятствия (летит напролом)
        """
        self.path = [(self.source.center_x, self.source.center_y)]
        self.current_waypoint = 0

    def calculate_path_to_destination(self):
        """
        Вычисляет путь к приемнику ресурсов

        Логика:
        - Аналогична calculate_path_to_source()
        - Создает путь от текущей позиции до приемника
        - Не обходит препятствия
        """
        self.path = [(self.destination.center_x, self.destination.center_y)]
        self.current_waypoint = 0

    def calculate_path_to_station(self):
        """
        Вычисляет путь обратно к станции

        Логика:
        - Создает путь от текущей позиции до станции
        - Кратчайший путь: сначала по X, потом по Y
        """
        self.path = [(self.core.center_x, self.core.center_y)]
        self.current_waypoint = 0

    def update(self, delta_time: float):
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
        if self.state == "WAITING_AT_STATION":
            if self.source:  # Взять задание
                self.setroute(self.source, self.destination)
        elif self.state == "FLYING_TO_SOURCE":
            self.movealongpath(delta_time)
            if self.distance_to(self.source) < DRONE_PICKUP_DISTANCE:
                self.state = "WAITING_AT_SOURCE"
        elif self.state == "WAITING_AT_SOURCE":
            if self.source.can_give_resource():
                self.take_resource(self.source)
                self.state = "FLYING_TO_DEST"
                self.calculate_path_to_destination()
        elif self.state == "FLYING_TO_DEST":
            self.move_along_path(delta_time)
            if self.distance_to(self.destination) < DRONE_DROP_DISTANCE:
                self.state = "WAITING_AT_DEST"
        elif self.state == "WAITING_AT_DEST":
            self.destination.add_drone_for_unload(self)  # Обработается в processqueues
            if not self.cargo:
                self.state = "RETURNING_TO_STATION"
                self.calculate_path_to_station()
        elif self.state == "RETURNING_TO_STATION":
            self.move_along_path(delta_time)
            if self.distance_to(self.core) < 32:
                self.state = "WAITING_AT_STATION"
                if self.station:
                    self.station.recover_drone(self)

    def move_along_path(self, delta_time: float):
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
        if self.current_waypoint < len(self.path):
            wx, wy = self.path[self.current_waypoint]
            angle = math.atan2(wy - self.center_y, wx - self.center_x)
            self.center_x += math.cos(angle) * self.speed * delta_time
            self.center_y += math.sin(angle) * self.speed * delta_time
            if self.reached_waypoint():
                self.current_waypoint += 1

    def distance_to(self, target: arcade.Sprite) -> float:
        """
        Вычисляет расстояние до цели

        Параметры:
        target: arcade.Sprite - цель для измерения расстояния

        Возвращает:
        float - расстояние в пикселях между центрами спрайтов
        """
        return ((self.center_x - target.center_x) ** 2 + (self.center_y - target.center_y) ** 2) ** 0.5

    def reached_waypoint(self) -> bool:
        """
        Проверяет, достиг ли дрон текущей точки пути

        Возвращает:
        bool - True если достиг текущей точки, False если нет

        Логика:
        - Сравнивает текущую позицию с целевой точкой
        - Если расстояние < 5 пикселей - считается достигшим
        """
        if self.current_waypoint < len(self.path):
            wx, wy = self.path[self.current_waypoint]
            return self.distance_to(arcade.SpriteSolidColor(1, 1, 1, (wx, wy))) < 5  # Fake sprite
        return True

    def take_resource(self, building):
        if building.can_give_resource():
            self.cargo = building.output_resource
            building.consume_resource(self.cargo)
            return True
        return False  # Новый метод

    def take_damage(self, amount: int):
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
        self.hp -= amount
        if self.hp <= 0:
            self.hp = 0
            if self.station:
                self.station.recover_drone(self)
            self.remove_from_queues()

    def remove_from_queues(self):
        """
        Удаляет дрона из всех очередей

        Логика:
        - Если есть source - удаляет из waiting_drones источника
        - Если есть destination - удаляет из waiting_for_unload приемника
        - Если есть станция - удаляет из всех связанных очередей
        """
        if self.source and self in self.source.waiting_drones:
            self.source.waiting_drones.remove(self)
        if self.destination and self in self.destination.waiting_for_unload:
            self.destination.waiting_for_unload.remove(self)

    def handle_building_destroyed(self, building: Building):
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
        if building == self.source or building == self.destination:
            if self.state in ["WAITING_AT_SOURCE", "TAKING_RESOURCE"]:
                self.state = "RETURNING_TO_STATION"
            elif self.state in ["WAITING_AT_DEST", "GIVING_RESOURCE"]:
                self.state = "RETURNING_TO_STATION"
            self.calculate_path_to_station()


class Bullet(arcade.Sprite):
    def __init__(self, filename: str, scale: float, x: float, y: float, angle: float, damage: int = 1, speed: float = 200.0):
        super().__init__(filename, scale)
        self.center_x = x
        self.center_y = y
        self.angle = math.degrees(angle)  # Arcade ожидает градусы
        self.damage = damage
        self.speed = speed

    def update(self, deltatime: float):
        super().update(deltatime)  # Стандартное движение Arcade
        # Проверка коллизии с врагами (в game.py или turret)
        # for enemy in self.core.enemy_list:  # Если добавишь core
        #     if arcade.check_for_collision(self, enemy):
        #         enemy.takedamage(self.damage)
        #         self.remove_from_sprite_lists()


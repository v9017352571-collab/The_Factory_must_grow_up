import arcade
from typing import Dict, Optional, Deque
from collections import deque
from resources import ResourceTransaction, ResourceStorage
from constants import good_bullet, bugs
from enemies import Bug

# Константы здоровья (из constants.py)
T_SIZE = 80
BUILDING_HP = {
    "Дрон-станция": 5,
    "Угольный бур": 5,
    "Электрический бур": 5,
    "Бронзовая плавильня": 5,
    "Кремнева плавильня": 5,
    "Завод микросхем": 5,
    "Завод боеприпасов": 5,
    "Медная турель": 5,
    "Бронзовая турель": 10,
    "Дальняя турель": 5,
    "Ядро": 20
}

RESOURCES_COST = {
    'Угольный бур': {'медь': 10, 'олово': 6, 'уголь': 0, 'бронза': 0, 'кремний': 0, 'боеприпас': 0},
    'Электрический бур': {'медь': 20, 'олово': 8, 'уголь': 0, 'бронза': 5, 'кремний': 5, 'боеприпас': 0},
    'Кремнева плавильня': {'медь': 12, 'олово': 5, 'уголь': 0, 'бронза': 0, 'кремний': 0, 'боеприпас': 0},
    'Бронзовая плавильня': {'медь': 30, 'олово': 14, 'уголь': 0, 'бронза': 0, 'кремний': 12, 'боеприпас': 0},
    'Завод боеприпасов': {'медь': 8, 'олово': 15, 'уголь': 0, 'бронза': 0, 'кремний': 24, 'боеприпас': 0},
    'Медная турель': {'медь': 32, 'олово': 16, 'уголь': 0, 'бронза': 0, 'кремний': 0, 'боеприпас': 0},
    'Бронзовая турель': {'медь': 14, 'олово': 6, 'уголь': 0, 'бронза': 10, 'кремний': 12, 'боеприпас': 0},
    'Длинноствольная турель': {'медь': 64, 'олово': 16, 'уголь': 0, 'бронза': 24, 'кремний': 10, 'боеприпас': 12},
    'Дроны': {'медь': 5, 'олово': 3, 'уголь': 0, 'бронза': 0, 'кремний': 1, 'боеприпас': 0}
}

RESOURCES_RECIPSES = {
    'Кремнева плавильня': {'input_resources': ('уголь'), 'output_resources': 'кремний'},
    'Бронзовая плавильня': {'input_resources': ('уголь', 'медь', 'олово'), 'output_resources': 'бронза'},
    'Завод боеприпасов': {'input_resources': ('уголь', 'олово', 'кремний'), 'output_resources': 'боеприпас'},
}

RESOURCES_SHOOTS = {
    'Медная турель': ('медь', 'уголь'),
    'Бронзовая турель': ('боеприпас'),
    'Длинноствольная турель': ('боеприпас', 'бронза')
}

BUILDINGS_TYPE = {
    'Угольный бур': 'Бур',
    'Электрический бур': 'Бур',
    'Кремнева плавильня': 'Завод',
    'Бронзовая плавильня': 'Завод',
    'Завод боеприпасов': 'Завод',
    'Медная турель': 'Турель',
    'Бронзовая турель': 'Турель',
    'Длинноствольная турель': 'Турель'
}

"""
Угольный бур - 10 медь, 6 олово, уголь, бронза, кремний, бп (потребляет: уголь, выдает: ресурс на котором стоит)

Электрический бур - 20 медь, 8 олово, уголь, 5 бронза, 5 кремний, бп (потребляет: None, выдает: ресурс на котором стоит)

Кремнева плавильня - 12 медь, 5 олово, уголь, бронза, кремний, бп (потребляет: уголь, выдает: кремний)

Бронзовая плавильня - 30 медь, 14 олово, уголь, бронза, 12 кремний, бп (потребляет: уголь, медь и олово, выдает: бронзу)

Завод боеприпасов - 8 медь, 15 олово, уголь, бронза, 24 кремний, бп (потребляет: уголь, олово и кремний, выдает: бп)

Медная турель - 32 медь,  16 олово, уголь, бронза, кремний, бп (потребляет: медь и уголь, выдает: 1 хп врагу)

Бронзовая турель - 14 медь, 6 олово, уголь, 10 бронза, 12 кремний, бп (потребляет: бп, выдает: 3 хп врагу)

Длинноствольная турель - 64 медь, 16 олово, уголь, 24 бронза, 10 кремний, 12 бп (потребляет: бп и бронзу, выдает: 5 хп врагу)

Дроны - 5 медь, 3 олово, 1 кремний

Ядро - бесценно (потребляет: None, выдает: уголь, медь, олово и кремний(последний с шансом в 10%))
"""


# =========== БАЗОВЫЙ КЛАСС Building ===========
class Building(arcade.Sprite, ResourceStorage):
    """Базовый класс для всех зданий"""

    def __init__(
            self,
            image_path: str,
            scale: float,
            x: float,
            y: float,
            name: str,
            capacity: Dict[str, int] | None
    ):
        arcade.Sprite.__init__(self, image_path, scale)
        ResourceStorage.__init__(self, capacity)

        # Основные свойства
        self.center_x = x
        self.center_y = y
        self.name = name

        # Здоровье
        self.max_hp = BUILDING_HP[name]
        self.hp = self.max_hp
        self.is_destroyed = False

        # Ресурсы
        # self.cost = cost
        self.cost = ResourceTransaction(RESOURCES_COST[self.name])

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

        if self.can_add(cargo, 1) and self.add(cargo, 1):
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
            for res, amt in self.get_all().items():
                if amt > 0:
                    needed = res
                    break
            if not needed:
                return False

        if self.has(needed, 1) and self.remove(needed, 1):
            drone.load(needed)
            return True
        return False

    def _destroy(self):
        """Полное уничтожение здания"""
        self.is_destroyed = True
        self.clear()

        # Оповещаем дронов
        for drone in list(self.attached_drones):
            drone.on_building_destroyed(self)
        self.attached_drones.clear()

        # Очищаем очереди
        self.waiting_drones.clear()
        self.waiting_unload.clear()

    # === ПУБЛИЧНЫЕ МЕТОДЫ ===

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
            "resources": str(self.get_all()),
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
            capacity=capacity,
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
            if not self.has("Уголь", 1):
                return
            # Тратим уголь
            self.remove("Уголь", 1)

        # Добываем ресурс
        self.add(self.resource_type, 1)


class CoalDrill(MineDrill):
    """Угольный бур - медленный, требует уголь"""

    def __init__(self, x: float, y: float, resource_type: str = "Медь"):
        super().__init__(
            image_path="Изображения/Здания/Буры/Бур.png",
            scale=0.25,
            x=x, y=y,
            drill_type="угольный",
            resource_type=resource_type,
            name="Угольный бур",
            needs_coal=True
        )


class ElectricDrill(MineDrill):
    """Электрический бур - быстрый, не требует топлива"""

    def __init__(self, x: float, y: float, resource_type: str = "Медь"):
        super().__init__(
            image_path="Изображения/Здания/Буры/Бур.png",
            scale=0.25,
            x=x, y=y,
            drill_type="электрический",
            resource_type=resource_type,
            name="Электрический бур",
            needs_coal=False
        )


# ----------- ПРОИЗВОДСТВЕННЫЕ ЗДАНИЯ -----------
class ProductionBuilding(Building):
    """Базовый класс для производств"""

    def __init__(
            self,
            image_path: str,
            scale: float,
            x: float, y: float,
            production_time: float,
            name: str
    ):

        self.input = RESOURCES_RECIPSES[name]['input_resources']
        self.output = RESOURCES_RECIPSES[name]['output_resources']
        capacity = {key: 10 for key in self.input}
        capacity[self.output] = 5

        super().__init__(
            image_path=image_path,
            scale=scale,
            x=x, y=y,
            name=name,
            capacity=capacity
        )

        self.production_time = production_time

    def _produce(self):
        """Производит выходной ресурс"""
        # 1. Проверяем все ли ингредиенты есть
        for ingredient in self.input:
            if not self.has(ingredient, 1):
                return  # Не хватает чего-то

        # 2. Проверяем есть ли место для продукта
        if not self.can_add(self.output, 1):
            return  # Нет места

        # 3. Забираем ингредиенты
        for ingredient in self.input:
            self.remove(ingredient, 1)

        # 4. Добавляем продукт
        self.add(self.output, 1)


class BronzeFurnace(ProductionBuilding):
    """Печь для бронзы"""

    def __init__(self, x: float, y: float):
        super().__init__(
            image_path="Изображения/Здания/Заводы/Печь.png",
            scale=0.25,
            x=x, y=y,
            production_time=2.0,
            name="Бронзовая плавильня"
        )
        self.hp = BUILDING_HP["Печь для бронзы"]
        self.max_hp = self.hp


class SiliconFurnace(ProductionBuilding):
    """Кремниевая печь"""

    def __init__(self, x: float, y: float):
        super().__init__(
            image_path="Изображения/Здания/Заводы/Печь.png",
            scale=0.25,
            x=x, y=y,
            production_time=2.0,
            name="Кремнева плавильня"
        )
        self.hp = BUILDING_HP["Кремниевая печь"]
        self.max_hp = self.hp


class AmmoFactory(ProductionBuilding):
    """Завод боеприпасов"""

    def __init__(self, x: float, y: float):
        super().__init__(
            image_path="Изображения/Здания/Заводы/Завод.png",
            scale=0.25,
            x=x, y=y,
            production_time=1.0,
            name="Завод боеприпасов"
        )


# ----------- ТУРЕЛИ -----------
class Turret(Building):
    """Базовый класс для турелей"""

    def __init__(
            self,
            base_image: str,
            tower_image: str,
            scale: float,
            x: float, y: float,
            damage: int,
            attack_range: float,  # в пикселях
            bullet_lifetime: float,
            bullet_speed: float,
            cooldown: float,
            ammo_per_shot: int,  # Сколько тратит за выстрел
            name: str
    ):
        capacity = {key: 10 for key in RESOURCES_SHOOTS[self.name]}
        super().__init__(
            image_path=base_image,
            scale=scale,
            x=x, y=y,
            name=name,
            capacity=capacity
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
        self.ammo_per_shot = ammo_per_shot
        self.resources_for_shoot = {key: 1 for key in RESOURCES_SHOOTS[self.name]}

        # Для поиска цели
        self.target = None


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
        if self.current_cooldown <= 0 and self.has(self.ammo_type, self.ammo_per_shot):
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
        if not self.remove_all(self.resources_for_shoot):
            return

        self.current_cooldown = self.cooldown_time

        good_bullet.append(ShotBullet(self, target=self.target))

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
        super().__init__(
            base_image="Изображения/Здания/Турели/РГ турель основание.png",
            tower_image="Изображения/Здания/Турели/РГ турель башня.png",
            scale=0.25,
            x=x, y=y,
            damage=1,
            attack_range=200,
            bullet_lifetime=3.0,
            bullet_speed=75.0,
            cooldown=1.0,
            ammo_per_shot=1,
            name="Медная турель"
        )


class BronzeTurret(Turret):
    """Бронзовая турель"""

    def __init__(self, x: float, y: float):
        super().__init__(
            base_image="Изображения/Здания/Турели/РГ турель основание.png",
            tower_image="Изображения/Здания/Турели/РГ турель башня.png",
            scale=0.25,
            x=x, y=y,
            damage=2,
            attack_range=250,
            bullet_lifetime=3.5,
            bullet_speed=87.5,
            cooldown=0.7,
            ammo_per_shot=1,
            name="Бронзовая турель"
        )


class LongRangeTurret(Turret):
    """Дальняя турель"""

    def __init__(self, x: float, y: float):
        super().__init__(
            base_image="Изображения/Здания/Турели/РГ турель основание.png",
            tower_image="Изображения/Здания/Турели/РГ турель башня.png",
            scale=0.25,
            x=x, y=y,
            damage=6,
            attack_range=400,
            bullet_lifetime=4.0,
            bullet_speed=100.0,
            cooldown=2.0,
            ammo_per_shot=1,
            name="Длинноствольная турель"
        )


class ShotBullet(arcade.Sprite):
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


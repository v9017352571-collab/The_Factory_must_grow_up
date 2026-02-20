import arcade
import math
from typing import Any
from sprite_list import bad_bullet, buildings  # добавлен buildings
# from core import Core  # для проверки типа


T_SIZE = 80  # пикселей на клетку
SPRITE_SCALE = 0.25  # масштаб для 32px спрайтов (становится 16px)

class Bullet(arcade.Sprite):
    """Пуля, летящая от источника к цели"""

    def __init__(self, filename: str, scale: float, damage: int, lifetime: float,
                 source: Any, target: Any, speed: float = 300.0):
        super().__init__(filename, scale)
        self.damage = damage
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.source = source
        self.target = target
        self.speed = speed
        self.velocity = (0.0, 0.0)

        # Устанавливаем начальную позицию (от источника)
        if hasattr(source, 'tower_sprite'):
            # Для турелей, у которых есть tower_sprite
            self.center_x = source.tower_sprite.center_x
            self.center_y = source.tower_sprite.center_y
        else:
            self.center_x = source.center_x
            self.center_y = source.center_y

        self._set_velocity_towards_target()

    def _set_velocity_towards_target(self):
        """Вычисляет вектор скорости в направлении цели"""
        if self.target is None:
            self.velocity = (0, 0)
            return

        dx = self.target.center_x - self.center_x
        dy = self.target.center_y - self.center_y
        distance = math.sqrt(dx*dx + dy*dy)

        if distance == 0:
            self.velocity = (0, 0)
        else:
            norm_x = dx / distance
            norm_y = dy / distance
            self.velocity = (norm_x * self.speed, norm_y * self.speed)

    def update(self, delta_time: float):
        """Обновление пули"""
        self.lifetime -= delta_time
        self.center_x += self.velocity[0] * delta_time
        self.center_y += self.velocity[1] * delta_time
        # Если время жизни истекло, пуля будет удалена внешним кодом (в game.py)


class Bug(arcade.Sprite):
    """Базовый класс для всех врагов"""

    def __init__(self, filename: str, scale: float, x: float, y: float, core: Any,
                 hp: int, damage: int, speed: float, is_ranged: bool,
                 attack_range: float = 0, attack_cooldown_time: float = 1.0,
                 name: str = "Жук", targets_buildings: bool = False):
        super().__init__(filename, scale)
        self.center_x = x
        self.center_y = y
        self.core = core
        self.hp = hp
        self.max_hp = hp
        self.damage = damage
        self.speed = speed
        self.speed_pixels = speed * T_SIZE
        self.is_ranged = is_ranged
        self.attack_range = attack_range
        self.attack_cooldown_time = attack_cooldown_time
        self.attack_cooldown = 0.0
        self.name = name
        self.target = None
        self.targets_buildings = targets_buildings  # может ли атаковать здания

    def update(self, delta_time: float):
        if self.attack_cooldown > 0:
            self.attack_cooldown -= delta_time

        if self.target and hasattr(self.target, 'hp') and self.target.hp > 0:
            dx = self.center_x - self.target.center_x
            dy = self.center_y - self.target.center_y
            distance = math.hypot(dx, dy)

            if self.is_ranged:
                if distance <= self.attack_range and self.attack_cooldown <= 0:
                    self.attack_target(self.target)
            else:
                if distance <= T_SIZE:
                    if self.attack_cooldown <= 0:
                        self.attack_target(self.target)
                else:
                    self.move_towards_target(delta_time)
        else:
            self.find_target()
            self.move_towards_target(delta_time)

    def find_target(self):
        """Поиск ближайшей цели: игрок -> (опционально здание) -> ядро"""
        from sprite_list import players  # локальный импорт, чтобы избежать циклических зависимостей

        # 1. Ищем игрока
        if players:
            player = None
            min_dist = float('inf')
            for p in players:
                if p.hp > 0:
                    dx = self.center_x - p.center_x
                    dy = self.center_y - p.center_y
                    dist = math.hypot(dx, dy)
                    if dist < min_dist:
                        min_dist = dist
                        player = p
            if player:
                if self.is_ranged:
                    if min_dist <= self.attack_range:
                        self.target = player
                        return
                else:
                    if min_dist <= T_SIZE * 2:  # дальность привлечения ближнего боя
                        self.target = player
                        return

        # 2. Если враг может атаковать здания, ищем ближайшее
        if self.targets_buildings:
            nearest_building = None
            min_dist = float('inf')
            for b in buildings:
                if b.hp > 0 and not getattr(b, 'is_core', False):  # исключаем ядро, чтобы оно оставалось главной целью
                    dx = self.center_x - b.center_x
                    dy = self.center_y - b.center_y
                    dist = math.hypot(dx, dy)
                    if dist < min_dist:
                        min_dist = dist
                        nearest_building = b
            if nearest_building:
                if self.is_ranged:
                    if min_dist <= self.attack_range:
                        self.target = nearest_building
                        return
                else:
                    # Для ближнего боя здание может быть целью, даже если далеко (пойдет к нему)
                    self.target = nearest_building
                    return

        # 3. Если ничего не нашли, цель — ядро
        if self.core and self.core.hp > 0:
            self.target = self.core
        else:
            self.target = None

    def move_towards_target(self, delta_time: float):
        """Движение к текущей цели по прямой"""
        if self.target is None:
            return

        dx = self.target.center_x - self.center_x
        dy = self.target.center_y - self.center_y
        distance = math.hypot(dx, dy)

        if distance < 1:
            return

        norm_x = dx / distance
        norm_y = dy / distance
        self.center_x += norm_x * self.speed_pixels * delta_time
        self.center_y += norm_y * self.speed_pixels * delta_time

    def attack_target(self, target: Any):
        """Атака цели"""
        if self.is_ranged:
            bullet = Bullet(
                filename="Изображения/Остальное/Пуля.png",
                scale=SPRITE_SCALE,
                damage=self.damage,
                lifetime=5.0,
                source=self,
                target=target,
                speed=300.0
            )
            bad_bullet.append(bullet)
        else:
            if hasattr(target, 'take_damage'):
                target.take_damage(self.damage)

        self.attack_cooldown = self.attack_cooldown_time

    def take_damage(self, amount: int) -> bool:
        self.hp -= amount
        if self.hp <= 0:
            self.hp = 0
            return True
        return False

    def get_coords(self):
        return (self.center_x, self.center_y)


# Конкретные виды жуков
class Beetle(Bug):
    def __init__(self, x: float, y: float, core: Any):
        super().__init__(
            filename="Изображения/Жуки/Обычный/Жук.png",
            scale=SPRITE_SCALE, x=x, y=y, core=core,
            hp=1, damage=1, speed=3.0, is_ranged=False,
            attack_cooldown_time=0.5, name="Обычный жук",
            targets_buildings=False
        )

class ArmoredBeetle(Bug):
    def __init__(self, x: float, y: float, core: Any):
        super().__init__(
            filename="Изображения/Жуки/Крепкий/Жук брониосиц.png",
            scale=SPRITE_SCALE, x=x, y=y, core=core,
            hp=3, damage=1, speed=1.0, is_ranged=False,
            attack_cooldown_time=0.5, name="Броненосец",
            targets_buildings=True   # может атаковать здания
        )

class SpittingBeetle(Bug):
    def __init__(self, x: float, y: float, core: Any):
        super().__init__(
            filename="Изображения/Жуки/Плевака/Жук плевака.png",
            scale=SPRITE_SCALE, x=x, y=y, core=core,
            hp=1, damage=2, speed=2.0, is_ranged=True,
            attack_range=5 * T_SIZE, attack_cooldown_time=2.0,
            name="Жук-плевок",
            targets_buildings=False
        )

class DominicTorettoBeetle(Bug):
    def __init__(self, x: float, y: float, core: Any):
        super().__init__(
            filename="Изображения/Жуки/Доминико/Жук доминико.png",  # уточните путь
            scale=SPRITE_SCALE, x=x, y=y, core=core,
            hp=2, damage=2, speed=3.0, is_ranged=False,
            attack_cooldown_time=0.5, name="Доминико Торетто",
            targets_buildings=False
        )

class HarkerBeetle(Bug):
    def __init__(self, x: float, y: float, core: Any):
        super().__init__(
            filename="Изображения/Жуки/Харкатель/Харкатель (2).png",
            scale=SPRITE_SCALE, x=x, y=y, core=core,
            hp=2, damage=3, speed=1.0, is_ranged=True,
            attack_range=7 * T_SIZE, attack_cooldown_time=3.0,
            name="Жук-харкатель",
            targets_buildings=True   # может атаковать здания
        )
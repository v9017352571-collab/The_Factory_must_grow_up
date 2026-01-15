# enemies.py
import arcade
from typing import List, Dict, Optional, Any
from constants import TILE_SIZE, SPRITE_SCALE


class Bug(arcade.Sprite):
    """Базовый класс для всех врагов"""

    def __init__(self, filename: str, scale: float, hp: int, damage: int, speed: float,
                 is_ranged: bool, name: str = "Жук", cores = None):
        """
        Инициализация жука

        Параметры:
        filename: str - путь к изображению (32x32 пикселей)
        scale: float - масштаб (0.5 для 16px)
        hp: int - здоровье жука
        damage: int - урон по целям
        speed: float - скорость в блоках в секунду
        is_ranged: bool - является ли дальнобойным
        name: str = "Жук" - название для отладки

        Атрибуты:
        self.speed_pixels: float - скорость в пикселях в секунду (блок = 16 пикселей)
        self.is_ranged: bool - флаг дальнобойной атаки
        self.target: Any = None - текущая цель
        self.attack_cooldown: float = 0.0 - таймер атаки в секундах
        self.bullet_list: arcade.SpriteList - список пуль для ranged жуков
        self.max_hp: int = hp - максимальное здоровье
        """
        super().__init__(filename, scale)
        self.hp = hp
        self.max_hp = hp
        self.damage = damage
        self.speed = speed
        self.speed_pixels = speed * 16.0
        self.is_ranged = is_ranged
        self.name = name
        self.target = None
        self.attack_cooldown = 0.0
        self.bullet_list = arcade.SpriteList()
        self.core = cores

    def update(self, delta_time: float):
        pass
        """
        Обновление состояния жука

        Параметры:
        delta_time: float - время с предыдущего кадра

        Логика:
        - Движение вниз к ядру
        - Проверка достижения ядра
        - Атака целей при возможности
        - Обновление пуль для ranged жуков
        """

    def move_towards_core(self, delta_time: float, core_y: float):
        pass
        """
        Движение жука в сторону ядра

        Параметры:
        delta_time: float - время с предыдущего кадра
        core_y: float - Y координата ядра

        Логика:
        - Уменьшает Y координату со скоростью speed_pixels
        - При достижении ядра начинает атаку
        - Все жуки двигаются строго вертикально
        """

    def attack_target(self, target: Any):
        pass
        """
        Атака цели

        Параметры:
        target: Any - цель для атаки (ядра, здание, игрок)

        Логика:
        - Для ближних жуков: наносит урон мгновенно
        - Для дальних жуков: создает пулю вместо прямого урона
        - Сбрасывает таймер атаки
        """

    def take_damage(self, amount: int) -> bool:
        pass
        """
        Получение урона жуком

        Параметры:
        amount: int - количество урона

        Возвращает:
        bool - True если жук умер, False если еще жив

        Особенности:
        - Уменьшает HP
        - При смерти удаляет жука из списка
        - Нет выпадения ресурсов при смерти (по ТЗ)
        """


class Beetle(Bug):
    """Обычный жук - слабый, быстрый, ближний бой"""

    def __init__(self, filename: str, scale: float, core):
        """
        Инициализация обычного жука

        Параметры:
        filename: str - путь к изображению
        scale: float - масштаб

        Атрибуты:
        self.hp: int = 1 - здоровье
        self.damage: int = 1 - урон
        self.speed: float = 3.0 - скорость в блоках/сек
        self.is_ranged: bool = False - ближний бой
        self.name: str = "Обычный жук"
        """
        super().__init__(filename, scale, hp=1, damage=1, speed=3.0,
                         is_ranged=False, name="Обычный жук", cores=core)


class ArmoredBeetle(Bug):
    """Жук броненосец - медленный, прочный, ближний бой"""

    def __init__(self, filename: str, scale: float, core):
        """
        Инициализация жука броненосца

        Параметры:
        filename: str - путь к изображению
        scale: float - масштаб

        Атрибуты:
        self.hp: int = 3 - здоровье
        self.damage: int = 1 - урон
        self.speed: float = 1.0 - скорость в блоках/сек
        self.is_ranged: bool = False - ближний бой
        self.name: str = "Броненосец"
        """
        super().__init__(filename, scale, hp=3, damage=1, speed=1.0,
                         is_ranged=False, name="Броненосец", cores=core)


class SpittingBeetle(Bug):
    """Жук-плевок - средний урон, дальний бой"""

    def __init__(self, filename: str, scale: float, core):
        """
        Инициализация жука-плевка

        Параметры:
        filename: str - путь к изображению
        scale: float - масштаб

        Атрибуты:
        self.hp: int = 1 - здоровье
        self.damage: int = 2 - урон
        self.speed: float = 2.0 - скорость в блоках/сек
        self.is_ranged: bool = True - дальний бой
        self.name: str = "Жук-плевок"
        self.bullet_range: int = 5 - дальность стрельбы в блоках
        self.bullet_cooldown: float = 2.0 - перезарядка в секундах
        """
        super().__init__(filename, scale, hp=1, damage=2, speed=2.0,
                         is_ranged=True, name="Жук-плевок", cores=core)


class DominicTorettoBeetle(Bug):
    """Жук Доминико Торетто - быстрый, средний урон, ближний бой"""

    def __init__(self, filename: str, scale: float, core):
        """
        Инициализация жука Доминико Торетто

        Параметры:
        filename: str - путь к изображению
        scale: float - масштаб

        Атрибуты:
        self.hp: int = 2 - здоровье
        self.damage: int = 2 - урон
        self.speed: float = 3.0 - скорость в блоках/сек
        self.is_ranged: bool = False - ближний бой
        self.name: str = "Доминико Торетто"
        """
        super().__init__(filename, scale, hp=2, damage=2, speed=3.0,
                         is_ranged=False, name="Доминико Торетто", cores=core)


class HarkerBeetle(Bug):
    """Жук-харкатель - высокий урон, медленный, дальний бой"""

    def __init__(self, filename: str, scale: float, core):
        """
        Инициализация жука-харкателя

        Параметры:
        filename: str - путь к изображению
        scale: float - масштаб

        Атрибуты:
        self.hp: int = 2 - здоровье
        self.damage: int = 3 - урон
        self.speed: float = 1.0 - скорость в блоках/сек
        self.is_ranged: bool = True - дальний бой
        self.name: str = "Жук-харкатель"
        self.bullet_range: int = 7 - дальность стрельбы в блоках
        self.bullet_cooldown: float = 3.0 - перезарядка в секундах
        """
        super().__init__(filename, scale, hp=2, damage=3, speed=1.0,
                         is_ranged=True, name="Жук-харкатель", cores=core)


class Bullet(arcade.Sprite):
    """Базовый класс для всех пуль в игре"""

    def __init__(self, filename: str, scale: float, damage: int, lifetime: float,
                 source: Any, target: Any, speed: float = 300.0):
        """
        Инициализация пули

        Параметры:
        filename: str - путь к изображению пули (32x32 пикселей)
        scale: float - масштаб изображения (0.5 для 16px)
        damage: int - урон по цели при попадании
        lifetime: float - время жизни пули в секундах
        source: Any - источник выстрела (турель или жук)
        target: Any - цель выстрела (жук, ядро, игрок, здание)
        speed: float = 300.0 - скорость пули в пикселях в секунду

        Атрибуты:
        self.damage: int - урон по цели
        self.lifetime: float - оставшееся время жизни в секундах
        self.max_lifetime: float - максимальное время жизни
        self.source: Any - источник выстрела
        self.target: Any - текущая цель
        self.speed: float - скорость движения в пикселях/сек
        self.velocity: Tuple[float, float] - вектор скорости
        """
        super().__init__(filename, scale)
        self.damage = damage
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.source = source
        self.target = target
        self.speed = speed
        self.velocity = (0.0, 0.0)

        # Устанавливаем начальную позицию и направление
        if hasattr(source, 'tower_sprite'):
            # Это турель - используем позицию башни
            self.center_x = source.tower_sprite.center_x
            self.center_y = source.tower_sprite.center_y
        else:
            # Обычный источник
            self.center_x = source.center_x
            self.center_y = source.center_y

        self.set_velocity_towards_target()

    def set_velocity_towards_target(self):
        pass
        """
        Вычисляет вектор скорости в направлении цели

        Логика:
        - Находит вектор от источника к цели
        - Нормализует вектор
        - Умножает на скорость пули
        - Устанавливает velocity
        """

    def update(self, delta_time: float):
        pass
        """
        Обновление состояния пули

        Параметры:
        delta_time: float - время с предыдущего кадра

        Логика:
        - Уменьшает время жизни на delta_time
        - Двигается в направлении цели
        - Проверяет столкновения с целью
        - Удаляется при истечении времени жизни
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

    def hit_target(self):
        pass
        """
        Обработка попадания пули в цель

        Логика:
        - Если цель имеет метод take_damage() - наносит урон
        - Удаляет пулю после попадания
        """
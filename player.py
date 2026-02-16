# player.py
import arcade
from typing import Optional, Any
from config import T_SIZE, SPRITE_SCALE, PLAYER_PICKUP_DISTANCE, PLAYER_DROP_DISTANCE, PLAYER_SPEED


class Player(arcade.Sprite):
    """Класс игрока - космический аппарат"""

    def __init__(self, filename: str, scale: float, core: Any):
        """
        Инициализация игрока

        Параметры:
        filename: str - путь к изображению игрока (32x32 пикселей)
        scale: float - масштаб (0.5 для 16px)
        core: Any - ссылка на ядро для возрождения

        Атрибуты:
        self.core: Any - ссылка на ядро
        self.hp: int = 3 - здоровье игрока
        self.max_hp: int = 3 - максимальное здоровье
        self.speed: float = 16.0 - скорость в пикселях в секунду (1 блок/сек)
        self.is_dead: bool = False - флаг смерти
        self.respawn_timer: float = 0.0 - таймер возрождения в секундах
        self.max_respawn_timer: float = 5.0 - 5 секунд на возрождение
        self.cargo: Optional[str] = None - ресурс в инвентаре (только 1 ресурс)
        self.can_pickup_distance: float = PLAYER_PICKUP_DISTANCE - дистанция забора ресурсов (3 блока)
        self.can_drop_distance: float = PLAYER_DROP_DISTANCE - дистанция отдачи ресурсов (3 блока)
        self.invulnerable_timer: float = 0.0 - таймер неуязвимости после возрождения
        self.invulnerable_duration: float = 1.0 - длительность неуязвимости в секундах
        self.damage_cooldown: float = 0.0 - таймер перезарядки получения урона
        self.damage_cooldown_duration: float = 0.5 - задержка между получением урона
        """
        super().__init__(filename, scale)
        self.core = core
        self.hp = 3
        self.max_hp = 3
        self.speed = PLAYER_SPEED * T_SIZE  # 16 пикселей/сек
        self.is_dead = False
        self.respawn_timer = 0.0
        self.max_respawn_timer = 0.0  # Мгновенное возрождение
        self.cargo = None  # может нести только 1 ресурс
        self.can_pickup_distance = PLAYER_PICKUP_DISTANCE
        self.can_drop_distance = PLAYER_DROP_DISTANCE

        # Таймеры
        self.invulnerable_timer = 0.0
        self.invulnerable_duration = 1.0  # 1 секунда неуязвимости
        self.damage_cooldown = 0.0
        self.damage_cooldown_duration = 0.5  # 0.5 секунды между уроном

        # Движение
        self.dx = 0.0
        self.dy = 0.0

        # Устанавливаем начальную позицию над ядром
        self.center_x = core.center_x
        self.center_y = core.center_y + core.height + 32

    def update(self, delta_time: float):
        """
        Обновление состояния игрока

        Параметры:
        delta_time: float - время с предыдущего кадра в секундах

        Логика:
        - Если мертв - обрабатывает возрождение
        - Если жив - обрабатывает движение
        - Проверяет столкновения с врагами
        - Обновляет позицию на экране
        """
        if self.is_dead:
            # Мгновенное возрождение
            self.respawn(self.core.game.map_height_pixels if hasattr(self.core.game, 'map_height_pixels') else 600)
            return

        # Обновляем таймеры
        if self.invulnerable_timer > 0:
            self.invulnerable_timer -= delta_time

        if self.damage_cooldown > 0:
            self.damage_cooldown -= delta_time

        # Движение
        self.center_x += self.dx * delta_time
        self.center_y += self.dy * delta_time

        # Проверяем границы карты
        self._check_bounds()

    def _check_bounds(self):
        """Проверяет границы карты и не дает игроку выйти за них"""
        if hasattr(self.core, 'game'):
            game = self.core.game
            if hasattr(game, 'map_width_pixels') and hasattr(game, 'map_height_pixels'):
                # Ширина и высота спрайта (примерно 16 пикселей)
                half_width = self.width / 2
                half_height = self.height / 2

                # Границы по X
                if self.center_x < half_width:
                    self.center_x = half_width
                elif self.center_x > game.map_width_pixels - half_width:
                    self.center_x = game.map_width_pixels - half_width

                # Границы по Y
                if self.center_y < half_height:
                    self.center_y = half_height
                elif self.center_y > game.map_height_pixels - half_height:
                    self.center_y = game.map_height_pixels - half_height

    def handle_movement(self, delta_time: float, pressed_keys: set):
        """
        Обработка движения игрока

        Параметры:
        delta_time: float - время с предыдущего кадра
        pressed_keys: set - множество нажатых клавиш

        Логика:
        - Читает нажатые клавиши (WASD или стрелки)
        - Обновляет позицию с учетом скорости и delta_time
        - Не выходит за границы карты
        - Скорость: 1 блок/сек (16 пикселей/сек)
        """
        if self.is_dead:
            self.dx = 0
            self.dy = 0
            return

        # Сбрасываем скорости
        self.dx = 0
        self.dy = 0

        # Обработка клавиш движения (WASD)
        if arcade.key.W in pressed_keys or arcade.key.UP in pressed_keys:
            self.dy = self.speed
        if arcade.key.S in pressed_keys or arcade.key.DOWN in pressed_keys:
            self.dy = -self.speed
        if arcade.key.A in pressed_keys or arcade.key.LEFT in pressed_keys:
            self.dx = -self.speed
        if arcade.key.D in pressed_keys or arcade.key.RIGHT in pressed_keys:
            self.dx = self.speed

        # Нормализация диагонального движения
        if self.dx != 0 and self.dy != 0:
            self.dx *= 0.7071  # sqrt(2)/2
            self.dy *= 0.7071

    def check_enemy_collisions(self, bugs: arcade.SpriteList) -> bool:
        """
        Проверка столкновений с врагами

        Параметры:
        bugs: arcade.SpriteList - список всех жуков

        Возвращает:
        bool - True если игрок получил урон, False если нет

        Логика:
        - Проверяет расстояние до каждого жука
        - Если расстояние меньше 16 пикселей - столкновение
        - Если HP врага < HP игрока - враг уничтожается
        - Если HP врага >= HP игрока - игрок получает урон
        - Может атаковать только один жук за кадр
        """
        if self.is_dead or self.invulnerable_timer > 0 or self.damage_cooldown > 0:
            return False

        for bug in bugs:
            # Вычисляем расстояние между центрами
            dx = self.center_x - bug.center_x
            dy = self.center_y - bug.center_y
            distance = (dx ** 2 + dy ** 2) ** 0.5

            # Если расстояние меньше суммы радиусов (примерно 16 + 8 = 24 пикселя)
            if distance < 24:
                # Сравниваем HP
                if bug.hp < self.hp:
                    # Игрок сильнее - уничтожаем врага
                    bug.take_damage(bug.hp)
                    return True
                else:
                    # Враг сильнее - игрок получает урон
                    self.take_damage(1)
                    return True

        return False

    def take_damage(self, amount: int):
        """
        Получение урона игроком

        Параметры:
        amount: int - количество урона

        Логика:
        - Уменьшает HP
        - Если HP <= 0 - начинает процесс возрождения
        - Не позволяет HP быть меньше 0
        """
        if self.is_dead or self.invulnerable_timer > 0 or self.damage_cooldown > 0:
            return

        # Устанавливаем кулдаун на получение урона
        self.damage_cooldown = self.damage_cooldown_duration

        # Уменьшаем HP
        self.hp = max(0, self.hp - amount)

        # Проверяем смерть
        if self.hp <= 0:
            self.start_respawn()

    def start_respawn(self):
        """
        Начало процесса возрождения

        Логика:
        - Помечает игрока как мертвого
        - Сбрасывает таймер возрождения
        - Сбрасывает HP для следующего возрождения
        - Блокирует управление во время возрождения
        """
        self.is_dead = True
        self.alpha = 128  # Полупрозрачный
        self.cargo = None  # Сбрасываем груз при смерти

    def respawn(self, map_height_pixels: int):
        """
        Возрождение игрока

        Параметры:
        map_height_pixels: int - высота карты в пикселях

        Логика:
        - Устанавливает позицию: x = core.center_x, y = core.center_y + 32
        - Помечает как живого
        - Восстанавливает HP до максимума (3 HP)
        - Разблокирует управление
        - Устанавливает неуязвимость на короткое время
        """
        # Устанавливаем позицию над ядром
        self.center_x = self.core.center_x
        self.center_y = self.core.center_y + 32

        # Восстанавливаем состояние
        self.is_dead = False
        self.hp = self.max_hp
        self.alpha = 255  # Полная непрозрачность

        # Устанавливаем неуязвимость
        self.invulnerable_timer = self.invulnerable_duration

        # Сбрасываем движение
        self.dx = 0
        self.dy = 0

    def pickup_resource(self, building: 'Building') -> bool:
        """
        Подбор ресурса из здания

        Параметры:
        building: Building - здание, из которого берется ресурс

        Возвращает:
        bool - True при успехе, False при неудаче

        Логика:
        - Проверяет расстояние до здания (≤ PLAYER_PICKUP_DISTANCE)
        - Проверяет, что у игрока нет груза (self.cargo is None)
        - Проверяет, что здание имеет ресурсы
        - Забирает один ресурс из здания
        - Устанавливает self.cargo = тип ресурса
        - Возвращает True при успехе, False при неудаче
        """
        if self.is_dead:
            return False

        # Проверяем расстояние
        dx = self.center_x - building.center_x
        dy = self.center_y - building.center_y
        distance = (dx ** 2 + dy ** 2) ** 0.5

        if distance > self.can_pickup_distance:
            return False

        # Проверяем, что у игрока нет груза
        if self.cargo is not None:
            return False

        # Проверяем, что здание может отдать ресурс
        if not building.can_give_resource():
            return False

        # Получаем тип ресурса из здания
        # Предполагаем, что здание имеет метод get_resource_type()
        if hasattr(building, 'output_resource'):
            resource_type = building.output_resource
        else:
            # Для ядра или других зданий
            for res, amount in building.resources.items():
                if amount > 0:
                    resource_type = res
                    break
            else:
                return False

        # Пытаемся забрать ресурс
        if building.consume_resource(resource_type, 1):
            self.cargo = resource_type
            return True

        return False

    def drop_resource(self, building: 'Building') -> bool:
        """
        Отдача ресурса в здание

        Параметры:
        building: Building - здание, в которое отдаётся ресурс

        Возвращает:
        bool - True при успехе, False при неудаче

        Логика:
        - Проверяет расстояние до здания (≤ PLAYER_DROP_DISTANCE)
        - Проверяет, что у игрока есть груз (self.cargo is not None)
        - Проверяет, что здание может принять ресурс
        - Отдает ресурс в здание
        - Очищает self.cargo (ставит None)
        - Возвращает True при успехе, False при неудаче
        """
        if self.is_dead:
            return False

        # Проверяем расстояние
        dx = self.center_x - building.center_x
        dy = self.center_y - building.center_y
        distance = (dx ** 2 + dy ** 2) ** 0.5

        if distance > self.can_drop_distance:
            return False

        # Проверяем, что у игрока есть груз
        if self.cargo is None:
            return False

        # Проверяем, что здание может принять ресурс
        if not building.can_accept(self.cargo):
            return False

        # Пытаемся отдать ресурс
        if building.accept_resource(self.cargo):
            self.cargo = None
            return True

        return False

    def is_invulnerable(self) -> bool:
        """
        Проверяет, неуязвим ли игрок в данный момент

        Возвращает:
        bool - True если неуязвим, False если уязвим
        """
        return self.invulnerable_timer > 0

    def draw(self):
        """
        Отрисовка игрока с эффектом неуязвимости (мигание)
        """
        if self.is_invulnerable():
            # Мигание при неуязвимости (50% времени видим)
            import time
            visible = int(time.time() * 10) % 2 == 0
            if visible:
                super().draw()
        else:
            super().draw()
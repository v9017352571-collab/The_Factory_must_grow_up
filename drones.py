import arcade
import math


class Drone(arcade.Sprite):
    """Простой дрон челночит между двумя зданиями"""

    def __init__(self, scale: float, x: float, y: float):
        super().__init__("Изображения/Остальное/Дрон.png", scale)
        self.center_x = x
        self.center_y = y

        # Маршрут
        self.source = None
        self.destination = None

        # Груз
        self.cargo = None  # Тип ресурса или None
        self.speed = 100.0

        # Состояние
        self.state = "to_source"  # to_source, loading, to_dest, unloading
        self.target_x = x
        self.target_y = y

        self.hp = 2
        self.max_hp = 2

    def set_route(self, source, destination):
        """Установить маршрут"""
        self.source = source
        self.destination = destination

        # Регистрируемся в зданиях
        source.attach_drone(self)
        destination.attach_drone(self)

        # Летим к источнику
        self.state = "to_source"
        self.target_x = source.center_x
        self.target_y = source.center_y
        self.cargo = None

    def update(self, delta_time: float):
        """Обновление движения"""
        if not self.source or not self.destination:
            return

        # Движение к цели
        self._move_to_target(delta_time)

        # Проверка достижения
        self._check_arrival()

    def _move_to_target(self, delta_time: float):
        """Движение к текущей цели"""
        dx = self.target_x - self.center_x
        dy = self.target_y - self.center_y
        distance = math.sqrt(dx * dx + dy * dy)

        if distance < 2:  # Почти достигли
            self.center_x = self.target_x
            self.center_y = self.target_y
            return

        # Двигаемся
        move = min(distance, self.speed * delta_time)
        self.center_x += dx / distance * move
        self.center_y += dy / distance * move

    def _check_arrival(self):
        """Проверяем достигли ли цели"""
        if self.state == "to_source" and self._is_at(self.source):
            self.state = "loading"
            self.source.drone_wants_load(self)

        elif self.state == "to_dest" and self._is_at(self.destination):
            self.state = "unloading"
            self.destination.drone_wants_unload(self)

    def _is_at(self, building, threshold: float = 10.0) -> bool:
        """Проверка достижения здания"""
        dx = self.center_x - building.center_x
        dy = self.center_y - building.center_y
        return math.sqrt(dx * dx + dy * dy) <= threshold

    def load(self, resource: str):
        """Загрузить ресурс"""
        self.cargo = resource
        self.state = "to_dest"
        self.target_x = self.destination.center_x
        self.target_y = self.destination.center_y

    def unload(self):
        """Разгрузить ресурс"""
        self.cargo = None
        self.state = "to_source"
        self.target_x = self.source.center_x
        self.target_y = self.source.center_y

    def get_cargo(self):
        """Что везём?"""
        return self.cargo

    def get_needed_resource(self):
        """Какой ресурс хотим забрать?"""
        # Если уже что-то везём - ничего не нужно
        if self.cargo:
            return None

        # Запрашиваем первый доступный ресурс из источника
        for res, amt in self.source.storage.get_all().items():
            if amt > 0:
                return res
        return None

    def is_close_to(self, building, max_dist: float = 32.0) -> bool:
        """Проверка близости к зданию"""
        dx = self.center_x - building.center_x
        dy = self.center_y - building.center_y
        return (dx * dx + dy * dy) <= (max_dist * max_dist)

    def on_building_destroyed(self, building):
        """Обработка разрушения здания"""
        if building == self.source or building == self.destination:
            # Маршрут нарушен - уничтожаем дрона
            self.hp = 0
            if self.source:
                self.source.detach_drone(self)
            if self.destination:
                self.destination.detach_drone(self)

    def take_damage(self, amount: int) -> bool:
        """Получить урон"""
        self.hp = max(0, self.hp - amount)
        return self.hp <= 0
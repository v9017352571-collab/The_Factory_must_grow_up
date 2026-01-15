# game.py
import arcade
from arcade.camera import Camera2D
from arcade.gui import UIManager
import math
import random
from constants import TILE_SIZE, SPRITE_SCALE, WAVES, BUILDING_HP, BUILDING_KEYS, BAGS
from core import Core, ResourceCost
from player import Player
from buildings import (Building, ElectricDrill,
                       BronzeFurnace, SiliconFurnace, AmmoFactory,
                       CopperTurret, BronzeTurret, LongRangeTurret, Drone)
from enemies import (Bug, Beetle, ArmoredBeetle, SpittingBeetle,
                     DominicTorettoBeetle, HarkerBeetle)


class MyGame(arcade.Window):
    """Основной класс игры - управляет всем игровым процессом"""

    def __init__(self, width: int, height: int, title: str):
        """
        Инициализация игры

        Параметры:
        width: int - ширина окна в пикселях
        height: int - высота окна в пикселях
        title: str - заголовок окна

        Атрибуты инициализации:
        self.width/height: int - размеры окна
        self.title: str - заголовок

        Атрибуты камер:
        self.world_camera: Camera2D - камера для игрового мира (следует за игроком)
        self.gui_camera: Camera2D - камера для UI (фиксированная, не двигается)

        Игровые сущности:
        self.player: Player - космический корабль игрока
        self.core: Core - ядро, которое нужно защитить
        self.buildings: arcade.SpriteList - все здания в игре
        self.bullets: arcade.SpriteList - все пули (турелей и жуков)
        self.bugs: arcade.SpriteList - все враги
        self.drones: arcade.SpriteList - все дроны

        Параметры карты (берутся из константы JSON):
        self.map_width: int - ширина карты в калетках
        self.map_height: int - высота карты в клетках
        self.map_width_pixels: int - ширина карты в пикселях
        self.map_height_pixels: int - высота карты в пикселях

        Система волн (берется из константы WAVES):
        self.waves: List[List[Any]] - расписание волн [[время_до_волны, [типы_жуков]], ...]
        self.current_wave_index: int - индекс текущей волны
        self.wave_timer: float - таймер до следующей волны в секундах

        Система строительства:
        self.selected_building_type: Optional[str] = None - выбранный тип здания для постройки
        self.delete_mode: bool = False - режим сноса зданий
        Тут я пока не до конца понимаю что делать
        self.programming_station: Optional[DroneStation] = None - ядро в режиме программирования
        self.programming_step: int = 0 - шаг программирования (0-неактивно, 1-выбран источник, 2-выбран приемник)
        self.programming_source: Optional[Building] = None - источник для программирования
        self.programming_destination: Optional[Building] = None - приемник для программирования

        Состояние игры:
        self.game_state: str = "playing" - текущее состояние ('playing', 'game_over', 'victory')
        self.hovered_building: Optional[Building] = None - здание под курсором для отображения информации
        self.pressed_keys: set = set() - множество нажатых клавиш для обработки движения

        UI система:
        self.ui_manager: UIManager - менеджер пользовательского интерфейса
        self.info_text: str = "" - текст информации для отображения
        self.info_position: Tuple[float, float] = (0, 0) - позиция текста информации
        """
        super().__init__(width, height, title)

        # Инициализация камер
        self.world_camera = Camera2D()

        # Инициализация игровых сущностей
        self.players = arcade.SpriteList()
        self.buildings = arcade.SpriteList()
        self.bugs = arcade.SpriteList()

        # Система волн (загружается из константы WAVES)
        self.waves = WAVES
        self.current_wave_index = 0
        self.wave_timer = 0.0

        # Состояние игры
        self.game_state = "playing"
        self.pressed_keys = set()
        self.grid = None # сетка со зданиями и т.п. на будущее

        # Загрузка карты и настройка
        self.load_map()
        self.setup()

    def load_map(self):
        """
        Загрузка карты из данных константы JSON

        Логика:
        - Использует глобальную константу JSON, загруженную из БД
        - Создает сетку карты на основе ширины и высоты
        - Размещает ядро в указанной позиции
        - Устанавливает точку спавна врагов
        - Инициализирует месторождения руд для буров
        - Устанавливает начальные ресурсы ядра
        """

        # Создаем сетку карты
        self.map = arcade.load_tilemap(":resources:/tiled_maps/level_1.json", scaling=0.5)
        self.map_width = int(self.map.width)
        self.map_height = int(self.map.height)
        self.map_width_pixels = self.map_width * TILE_SIZE
        self.map_height_pixels = self.map_height * TILE_SIZE
        self.grid = [[None for _ in range(self.map_width)] for _ in range(self.map_height)]

    def setup_ui(self):
        """
        Настройка пользовательского интерфейса

        Создает и позиционирует все UI элементы:
        1. Панель постройки зданий внизу экрана
        2. Информационную панель для отображения ресурсов
        3. Кнопки управления

        Структура UI:
        - Нижняя панель: кнопки для выбора типов зданий
        - Левая панель: отображение ресурсов ядра и HP
        - Верхняя панель: информация о состоянии игры

        Каждая кнопка привязана к обработчику событий для соответствующего действия.
        """
        pass
    def setup(self):
        """
        Полная инициализация игры после создания окна

        Порядок инициализации:
        1. Создание игрока
        2. Добавление ядра в список зданий
        3. Инициализация таймеров
        4. Установка начального состояния
        5. Загрузка ресурсов спрайтов

        Этот метод вызывается после создания окна и загрузки карты,
        готовит игру к запуску.
        """
        self.core = Core("Изображения\Здания\Ядро (2).png", SPRITE_SCALE, 200, 200)
        self.buildings.append(self.core)
        self.player = Player("Изображения\Остальное\Нгг.png", SPRITE_SCALE, self.core)
        self.players.append(self.player)
        self.wave_timer = self.waves[0][0] if self.waves else 180.0


    def on_update(self, delta_time: float):
        """
        Основной метод обновления состояния игры каждый кадр

        Параметры:
        delta_time: float - время с предыдущего кадра в секундах

        Порядок обновления:
        1. Обновление камер
        2. Обновление игрока
        3. Обновление всех зданий
        4. Обновление всех дронов
        5. Обновление всех жуков
        6. Обновление всех пуль
        7. Обработка системы волн
        8. Обработка передачи ресурсов
        9. Проверка состояния игры
        10. Обновление UI

        Ключевые системы:
        - Система волн: управляет спавном врагов по расписанию
        - Система дронов: управляет доставкой ресурсов
        - Система столкновений: проверяет столкновения пуль с целями
        - Система ресурсов: управляет производством и передачей ресурсов
        """
        if self.game_state != "playing":
            return

            # Обновление игрока
        if self.players:
            self.player.update(delta_time, self.pressed_keys)

        position = (
            self.player.center_x,
            self.player.center_y
        )
        self.world_camera.position = arcade.math.lerp_2d(  # Изменяем позицию камеры
            self.world_camera.position,
            position,
            0.5,  # Плавность следования камеры
        )

        #self.wave_timer += delta_time

        # if self.wave_timer >= self.waves[self.current_wave_index][0]:
        #     for bug in self.waves[self.current_wave_index][2]:
        #         BAGS[bug]()
        #потом доделаю

    def update_waves(self, delta_time: float):
        """
        Обновление системы волн врагов

        Логика работы:
        1. Уменьшает таймер до следующей волны
        2. При достижении нуля запускает спавн волны
        3. Управляет плавным спавном жуков внутри волны

        Алгоритм спавна:
        - Первый жук спавнится сразу при начале волны
        - Последующие жуки спавнятся с интервалом 1 секунда
        - После спавна всех жуков устанавливается таймер до следующей волны

        Обработка окончания волн:
        - Если все волны пройдены и нет жуков на карте -> победа
        """
        pass

    def spawn_bug(self, bug_type: str):
        """
        Спавн одного жука

        Параметры:
        bug_type: str - тип жука на русском
            • "Обычный жук"
            • "Броненосец"
            • "Жук-плевок"
            • "Доминико Торетто"
            • "Жук-харкатель"

        Процесс спавна:
        1. Создание соответствующего класса жука
        2. Установка позиции в рандомной позиции
        3. Добавление в bugs SpriteList
        """
        pass

    def on_draw(self):
        """
        Отрисовка игры

        Порядок отрисовки:
        1. Очистка экрана
        2. Активация world_camera
        3. Отрисовка фона карты
        4. Отрисовка сетки (для отладки)
        5. Отрисовка зданий
        6. Отрисовка дронов
        7. Отрисовка жуков
        8. Отрисовка пуль
        9. Активация gui_camera
        10. Отрисовка игрока (всегда в центре экрана)
        11. Отрисовка UI
        12. Отрисовка информации о здании
        13. Отрисовка экранов победы/поражения

        Важные принципы:
        • Сначала фон, потом объекты, потом UI
        • Камеры переключаются для разделения мира и интерфейса
        • Игрок всегда в центре экрана благодаря gui_camera
        • Информация отображается поверх всех элементов

        Оптимизация:
        • batch drawing для SpriteList
        • минимальное количество draw calls
        """
        self.clear()

        self.world_camera.use()


        # Рисуем здания
        self.buildings.draw()
        if self.players:
            self.players.draw()

    def on_mouse_press(self, x: float, y: float, button: int, modifiers: int):
        """
        Обработка нажатия мыши

        Преобразование координат:
        world_x = x + world_camera.position[0]
        world_y = y + world_camera.position[1]

        Логика обработки:
        1. Проверка UI элементов
        2. Режим сноса зданий
        3. Выбор типа здания
        4. Программирование дронов (режим трех кликов)
        5. Двойной клик по станции для переназначения

        Важные ограничения:
        • Нельзя снести ядро
        • Нельзя построить на занятом месте
        • Нельзя построить без ресурсов
        • Нельзя программировать без станции
        """
        pass

    def on_key_press(self, key: int, modifiers: int):
        """
        Обработка нажатия клавиш

        Управление игроком:
        • W/A/S/D или стрелки - движение

        Управление строительством:
        • Цифры 1-8 - выбор типа здания
        • DEL - переключение режима сноса
        • R - отмена текущего выбора здания

        Управление игрой:
        • ENTER - возврат в меню при победе/поражении
        • ESC - пауза
        """
        self.pressed_keys.add(key)

    def on_key_release(self, key: int, modifiers: int):
        """
        Обработка отпускания клавиш

        Основная логика:
        if key in pressed_keys:
            pressed_keys.remove(key)

        Специальные действия:
        • ESC в состоянии паузы - продолжение игры
        • ENTER в состоянии победы/поражения - возврат в меню
        """
        if key in self.pressed_keys:
            self.pressed_keys.remove(key)
    def check_game_state(self):
        """
        Проверка состояния игры

        Условия поражения:
        if core.hp <= 0:
            game_state = "game_over"

        Условия победы:
        if current_wave_index >= len(waves) and len(bugs) == 0:
            game_state = "victory"
        """
        pass

    def transfer_resources(self):
        """
        СИСТЕМА ПЕРЕДАЧИ РЕСУРСОВ ЧЕРЕЗ ДРОНОВ

        ВАЖНО: В этой версии НЕТ автоматической передачи ресурсов!
        Все ресурсы передаются ТОЛЬКО через дронов и игрока.
        """
        pass

    def draw_building_info(self):
        """
        Отрисовка информации о здании под курсором

        Логика:
        - Показывает название здания
        - Показывает текущие ресурсы внутри здания
        - Для ядра показывает количество ресурсов
        - Для других зданий показывает занятость и состояние
        """
        pass

    def draw_game_state_screen(self):
        """
        Отрисовка экрана победы/поражения

        Логика:
        - Показывает крупный текст "ВЫ ПРОИГРАЛИ" или "ВЫ ПОБЕДИЛИ"
        - Показывает инструкцию для продолжения (ENTER для возврата в меню)
        - Блокирует игровое управление
        """
        pass

    def destroy_building(self, building: Building):
        """
        Уничтожение здания и всех связанных элементов

        Параметры:
        building: Building - уничтожаемое здание

        Логика:
        1. Если это станция:
           - Уничтожает дрона
           - Вызывает recover_drone() для создания нового (если достаточно ресурсов)
        2. Если это источник/приемник для дронов:
           - Находит все дроны, которые работают с этим зданием
           - Для каждого дрона:
             * Удаляет из очередей
             * Уничтожает груз
             * Отправляет на станцию
        3. Удаляет здание из сетки и списков
        4. Возвращает половину стоимости в ядро
        """
        pass


#Тест
def main():
    window = MyGame(1000, 800, "Заводы и Тауэр Дефенс")
    arcade.run()

if __name__ == "__main__":
    main()
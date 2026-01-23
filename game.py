# game.py
import arcade
from arcade.camera import Camera2D
from arcade.gui import UIManager
import math
import random
from constants import T_SIZE, SPRITE_SCALE, WAVES, BUILDING_HP, BUILDING_KEYS, BAGS, players, buildings, bugs, \
    CAMERA_LERP, RESOURCES, TEXTYRE
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

        # Инициализация камер и т.п.
        self.world_camera = arcade.camera.Camera2D()
        self.gui_camera = arcade.camera.Camera2D()
        self.cam_target = (0, 0)

        # Система волн (загружается из константы WAVES)
        self.waves = WAVES
        self.current_wave_index = 0
        self.wave_timer = 120

        # Состояние игры
        self.game_state = "playing"
        self.pressed_keys = set()
        self.grid = None # Сетка со зданиями и т.п. на будущее

        self.player = None
        self.core = None
        self.rote_dron = False
        self.information_about_the_building = {}

        # Загрузка карты и настройка
        self.map_height_pixels = None
        self.map_width_pixels = None
        self.map_height = None
        self.map_width = None
        self.map = None
        self.setup()
        self.load_map()
        self.buildings = arcade.SpriteList()
        self.bullets = arcade.SpriteList()
        self.bugs = arcade.SpriteList()
        self.drones = arcade.SpriteList()
        self.grid = None
        self.resource_icons = arcade.SpriteList()


        def calculate_level_stats(self):
            """Вычисление статистики для текущего уровня"""
            return {
                'level_number': self.current_level,
                'score': self.calculate_score(),
                'enemies_killed': self.enemies_killed,
                'time_spent': self.game_time,
                'waves_completed': self.current_wave_index,
                'resources_collected': self.calculate_resources_collected(),
                'buildings_built': len(self.buildings),
                'drones_used': len(self.drones)
            }

        def on_victory(self):
            """Вызывается при победе на уровне"""
            level_stats = self.calculate_level_stats()

            # Сохраняем в общую статистику
            self.game_stats.add_level_result(level_stats)

            # Показываем соответствующее окно
            from menu import show_level_complete, show_final_results

            total_levels = 5  # Всего уровней в игре

            if self.current_level < total_levels:
                # Показываем окно завершения уровня
                show_level_complete(
                    level_data=level_stats,
                    user_id=self.current_user_id,
                    username=self.current_user
                )
            else:
                # Показываем финальное окно
                total_stats = self.game_stats.get_total_stats()
                show_final_results(
                    total_stats=total_stats,
                    user_id=self.current_user_id,
                    username=self.current_user
                )

        def on_defeat(self, reason: str = "Ядро разрушено"):
            """Вызывается при поражении"""
            from menu import show_game_over

            stats = {
                'score': self.calculate_score(),
                'enemies_killed': self.enemies_killed,
                'time_survived': self.game_time,
                'waves_completed': self.current_wave_index
            }

            show_game_over(
                level_number=self.current_level,
                reason=reason,
                stats=stats,
                user_id=self.current_user_id
            )

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
        self.map = arcade.load_tilemap(":resources:/tiled_maps/level_1.json")
        self.map_width = self.map.width
        self.map_height = self.map.height
        self.map_width_pixels = self.map_width * T_SIZE
        self.map_height_pixels = self.map_height * T_SIZE

    def setup_ui(self):
        """Создание UI элементов при инициализации"""
        window = arcade.get_window()

        # Таймер волны
        self.wave_timer_text = arcade.Text(
            text="0",
            x=window.width // 2,
            y=window.height - 20,
            color=arcade.color.WHITE,
            font_size=24,
            anchor_x="center",
            anchor_y="top"
        )

        # Кэш для загруженных текстур ресурсов
        self.resource_textures = {}

        # Кэш для текстовых объектов количества
        self.resource_count_texts = {}

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
        buildings.append(self.core)
        self.player = Player("Изображения\Остальное\Нгг.png", SPRITE_SCALE, self.core)
        players.append(self.player)
        self.setup_ui()

    def cam(self):
        cam_x, cam_y = self.world_camera.position
        dz_left = cam_x - 50 // 2
        dz_right = cam_x + 50 // 2
        dz_bottom = cam_y - 50 // 2
        dz_top = cam_y + 50 // 2

        px, py = self.player.center_x, self.player.center_y
        target_x, target_y = cam_x, cam_y

        if px < dz_left:
            target_x = px + 50 // 2
        elif px > dz_right:
            target_x = px - 50 // 2
        if py < dz_bottom:
            target_y = py + 50 // 2
        elif py > dz_top:
            target_y = py - 50 // 2

        # Не показываем «пустоту» за краями карты
        half_w = int(self.world_camera.viewport_width / 2)
        half_h = int(self.world_camera.viewport_height / 2)
        target_x = max(half_w, min(int(self.map_width_pixels) - half_w, target_x))
        target_y = max(half_h, min(int(self.map_height_pixels) - half_h, target_y))

        # Плавно к цели
        smooth_x = (1 - CAMERA_LERP) * cam_x + CAMERA_LERP * target_x
        smooth_y = (1 - CAMERA_LERP) * cam_y + CAMERA_LERP * target_y
        self.cam_target = (smooth_x, smooth_y)

        self.world_camera.position = (self.cam_target[0], self.cam_target[1])

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
        self.cam()

        if self.game_state != "playing":
            return

            # Обновление игрока
        if players:
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
        self.update_waves(delta_time)
        self.destroy_building()
        self.drone_destruction()

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
        self.wave_timer -= delta_time

        for bug in bugs:
            if bug.hp <= 0:
                bugs.remove(bug)


        if self.wave_timer <= 0:
            for bug in self.waves[self.current_wave_index]:
                if random.randint(0, 1):
                    x = random.randint(0, self.map_width_pixels)
                    y = 0
                else:
                    y = random.randint(0, self.map_height_pixels)
                    x = 0
                bugs.append(BAGS[bug](x, y))
                WAVES.remove(self.current_wave_index)
            self.wave_timer = 100


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
        self.ui_dr()
        bugs.draw()
        buildings.draw()
        if players:
            players.draw()

        self.gui_camera.use()

    def ui_dr(self):
        """Обновление и отрисовка UI каждый кадр"""
        window = self.world_camera


        # Обновление и отрисовка таймера волны
        self.wave_timer_text.text = str(int(self.wave_timer))
        self.wave_timer_text.draw()

        # Отступы для ресурсов
        right_margin = 60
        start_y = window.height - 60
        vertical_spacing = 45

        # Отрисовка ресурсов только если они есть
        if self.information_about_the_building:
            resources = self.information_about_the_building

            for i, (resource_name, amount) in enumerate(resources.items()):
                y_pos = start_y - i * vertical_spacing

                # 1. Создание иконки ресурса
                if resource_name in TEXTYRE:
                    # Создаем спрайт
                    sprite = arcade.Sprite(TEXTYRE[resource_name])
                    sprite.center_x = window.width - right_margin
                    sprite.center_y = y_pos
                    sprite.scale = 0.25  # Масштаб 0.25
                    self.resource_icons.append(sprite)

                # 2. Отрисовка количества
                if resource_name not in self.resource_count_texts:
                    self.resource_count_texts[resource_name] = arcade.Text(
                        text=str(amount),
                        x=window.width - right_margin - 40,
                        y=y_pos,
                        color=arcade.color.WHITE,
                        font_size=18,
                        anchor_x="center",
                        anchor_y="center"
                    )
                else:
                    self.resource_count_texts[resource_name].text = str(amount)
                    self.resource_count_texts[resource_name].x = window.width - right_margin - 40
                    self.resource_count_texts[resource_name].y = y_pos

                self.resource_count_texts[resource_name].draw()

        # Отрисовка всех иконок ресурсов
        self.resource_icons.draw()

    def on_mouse_motion(self, x, y, dx, dy):
        x1, y1 = self.world_camera.bottom_left
        x2 = (x + x1) // T_SIZE
        y2 = (y + y1) // T_SIZE
        x3, y3 = x2 * T_SIZE + T_SIZE // 2, y2 * T_SIZE + T_SIZE // 2
        for i in buildings:
            if i.center_x == x3 and i.center_y == y3:
                self.information_about_the_building = i.resources
                return
        self.information_about_the_building = {}



    def on_mouse_press(self, x: float, y: float, button: int, modifiers: int):
        """
        Обработка постройки зданий, сноса зданий, создания дронов с маршрутами
        и уничтожение дронов кликом.
        """
        #Постройка зданий
        if arcade.MOUSE_BUTTON_LEFT == button:
            self.build_building(x, y)

        #Создаем маршрут с дронами
        elif arcade.MOUSE_BUTTON_RIGHT == button: #Проверять кол рес
            self.f_rote_dron(x, y)

        #Удаляем дрон
        elif arcade.MOUSE_BUTTON_MIDDLE == button:
            self.del_dron(x, y)


    def build_building(self, x, y):
        x1, y1 = self.world_camera.bottom_left
        x2 = (x + x1) // T_SIZE
        y2 = (y + y1) // T_SIZE
        x3, y3 = x2 * T_SIZE + T_SIZE // 2, y2 * T_SIZE + T_SIZE // 2
        for i in self.pressed_keys:
            building = BUILDING_KEYS.get(i)
            for e in buildings:
                if e.center_x == x3 and e.center_y == y3:
                    return
            if building:
                buildings.append(building(x3, y3))
                return

            # Снос зданий

            if arcade.key.DELETE == i:
                for u in buildings:
                    if u.max_hp != 20:
                        if u.center_x == x3 and u.center_y == y3:
                            buildings.remove(u)
                            for res in u.cost:
                                u.cost[res] = int(u.cost[res] / 2)
                            return

    def f_rote_dron(self, x, y):
        x1, y1 = self.world_camera.bottom_left
        x2 = (x + x1) // T_SIZE
        y2 = (y + y1) // T_SIZE
        x3, y3 = x2 * T_SIZE + T_SIZE // 2, y2 * T_SIZE + T_SIZE // 2
        if self.core.center_x == x3 and self.core.center_y == y3:
            self.rote_dron = True
            return
        for t in buildings:
            if not t.max_hp == 20:
                if self.rote_dron and t.center_x == x3 and t.center_y == y3:
                    if self.rote_dron != True:
                        players.append(Drone(self.rote_dron.append(t)))
                        self.rote_dron = False
                        self.core.add_resource("Кремний", -3)
                        self.core.add_resource("Медь", -2)
                        self.core.add_resource("Олово", -1)
                        return
                    else:
                        self.rote_dron = [t]
                        return

    def del_dron(self, x, y):
        x1, y1 = self.gui_camera.bottom_left
        for dr in players:
            if dr.max_hp != 3:
                if (x + x1) - dr.center_x < 5 and (y + y1) - dr.center_y < 5:
                    players.remove(dr)
                    self.core.add_resource("Кремний", 2)
                    self.core.add_resource("Медь", 2)
                    break



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
        """
        if self.core.hp <= 0:
            self.game_state = "game_over"
        elif self.current_wave_index >= len(self.waves) and len(bugs) == 0:
            self.game_state = "victory"
        elif arcade.key.ESCAPE in self.pressed_keys:
            self.game_state = "pause"
    def destroy_building(self):
        """
        Уничтожение здания
        """
        for b in buildings:
            if b.hp <= 0:
                buildings.remove(b)

    def drone_destruction(self):
        """
        Уничтожение дронов
        """
        for b in players:
            if b.hp <= 0:
                players.remove(b)




#Тест
def main():
    window = MyGame(500, 500, "Заводы и Тауэр Дефенс")
    arcade.run()

if __name__ == "__main__":
    main()



class GameStats:
    """Класс для хранения и обработки статистики игры"""

    def __init__(self):
        self.level_results = []
        self.total_score = 0
        self.total_enemies_killed = 0
        self.total_play_time = 0.0
        self.levels_completed = 0

    def add_level_result(self, level_stats):
        """Добавляет результат уровня"""
        self.level_results.append(level_stats)
        self.total_score += level_stats.get('score', 0)
        self.total_enemies_killed += level_stats.get('enemies_killed', 0)
        self.total_play_time += level_stats.get('time_spent', 0)
        self.levels_completed += 1

    def get_total_stats(self):
        """Возвращает общую статистику"""
        return {
            'total_score': self.total_score,
            'total_enemies_killed': self.total_enemies_killed,
            'total_play_time': self.total_play_time,
            'levels_completed': self.levels_completed,
            'level_results': self.level_results
        }
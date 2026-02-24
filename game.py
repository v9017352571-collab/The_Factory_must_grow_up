# game.py
import arcade
from arcade.camera import Camera2D
from arcade.gui import UIManager
import math
import random

from arcade.math import rand_in_circle, rand_on_circle
from arcade.particles import Emitter, EmitBurst, LifetimeParticle

from constants import T_SIZE, SPRITE_SCALE, WAVES, BUILDING_HP, BUILDING_KEYS, BAGS, \
    CAMERA_LERP, RESOURCES, TEXTYRE, MUSIC_MENU, MUSIC_UNITED2, MUSIC_UNITED1, MUSIC_ATTACKS1, MUSIC_UNITED3, \
    MUSIC_ATTACKS2, MUSIC_ATTACKS3, HIT, JSON
from sprite_list import good_bullet, bad_bullet, players, buildings, bugs
from core import Core
from player import Player
from buildings import (Building, ElectricDrill,
                       BronzeFurnace, SiliconFurnace, AmmoFactory,
                       CopperTurret, BronzeTurret, LongRangeTurret, Drone)
from enemies import (Bug, Beetle, ArmoredBeetle, SpittingBeetle,
                     DominicTorettoBeetle, HarkerBeetle)

class MyGame(arcade.Window):
    """Основной класс игры - управляет всем игровым процессом"""

    def __init__(self, width: int, height: int, title: str):
        super().__init__(width, height, title)

        # Инициализация камер и т.п.
        self.txtt = None
        self.world_camera = arcade.camera.Camera2D()
        self.gui_camera = arcade.camera.Camera2D()
        self.cam_target = (0, 0)

        # Система волн (загружается из константы WAVES)
        self.waves = WAVES
        self.current_wave_index = 0
        self.wave_timer = 100

        # Состояние игры
        self.game_state = "game"
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
        self.emitters = []
        self.star_texture = arcade.load_texture("Изображения\Остальное\Пуля.png")
        self.orb_texture = arcade.load_texture("Изображения\Остальное\Камень.png")
        self.pausa_dui()
        self.game_time = 0.0  # время текущего уровня
        self.game_stats = GameStats()  # общая статистика за все уровни
        self.current_level = 1  # будет переопределено из меню
        self.current_user_id = None  # ID пользователя из БД
        self.current_user = None  # имя пользователя
        self.enemies_killed = 0  # убито на текущем уровне
        self.buildings_built = 0  # построено на уровне
        self.drones_used = 0  # создано дронов на уровне

    def calculate_level_stats(self):
        # Пока score и resources_collected можно оставить заглушками
        return {
            'level_number': self.current_level,
            'score': 0,  # можно добавить позже
            'enemies_killed': self.enemies_killed,
            'time_spent': self.game_time,
            'waves_completed': self.current_wave_index,
            'resources_collected': 0,  # заглушка
            'buildings_built': self.buildings_built,
            'drones_used': self.drones_used
        }

    def victory(self):
        level_stats = self.calculate_level_stats()
        self.game_stats.add_level_result(level_stats)

        # Сохраняем прогресс в БД (если есть пользователь)
        if self.current_user_id:
            from database import GameDatabase
            with GameDatabase() as db:
                db.save_level_record(self.current_user_id, level_stats)
                db.update_player_progress(self.current_user_id, self.current_level)

        # Проверяем, все ли уровни пройдены (всего 3)
        if self.current_level < 3:
            from menu import LevelCompleteWindow
            win = LevelCompleteWindow(
                level_data=level_stats,
                user_id=self.current_user_id,
                username=self.current_user,
                callback=self.handle_level_complete
            )
            win.show()
        else:
            from menu import FinalResultsWindow
            win = FinalResultsWindow(
                total_stats=self.game_stats.get_total_stats(),
                user_id=self.current_user_id,
                username=self.current_user,
                callback=self.handle_game_complete
            )
            win.show()
        self.close()

    def defeat(self, reason="Ядро разрушено"):
        from menu import GameOverWindow
        win = GameOverWindow(
            level_number=self.current_level,
            reason=reason,
            stats={
                'score': 0,
                'enemies_killed': self.enemies_killed,
                'time_survived': self.game_time,
                'waves_completed': self.current_wave_index
            },
            user_id=self.current_user_id,
            callback=self.handle_game_over
        )
        win.show()
        self.close()

    def handle_level_complete(self, action):
        if action == 'next_level':
            self.start_new_level(self.current_level + 1)
        elif action == 'retry_level':
            self.start_new_level(self.current_level)
        elif action == 'to_menu':
            from menu import StartMenuWindow
            StartMenuWindow(self.width, self.height, "Заводы и Тауэр Дефенс").show()

    def handle_game_over(self, action):
        if action == 'retry_level':
            self.start_new_level(self.current_level)
        elif action == 'to_menu':
            from menu import StartMenuWindow
            StartMenuWindow(self.width, self.height, "Заводы и Тауэр Дефенс").show()

    def handle_game_complete(self, action):
        if action == 'new_game':
            self.start_new_level(1)
        elif action == 'to_menu':
            from menu import StartMenuWindow
            StartMenuWindow(self.width, self.height, "Заводы и Тауэр Дефенс").show()

    def start_new_level(self, level):
        from game import MyGame
        game = MyGame(self.width, self.height, f"Уровень {level}")
        game.current_level = level
        game.current_user_id = self.current_user_id
        game.current_user = self.current_user
        game.setup()
        arcade.run()

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
        self.core = Core(SPRITE_SCALE, 200, 200)
        buildings.append(self.core)
        self.player = Player("Изображения\Остальное\Нгг.png", SPRITE_SCALE, self.core)
        players.append(self.player)
        self.ost = arcade.play_sound(random.choice([MUSIC_UNITED2, MUSIC_UNITED1, MUSIC_UNITED3]))
        self.ost_UNITED = True
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
        if self.game_state == 'game':
            self.game_time += delta_time
            self.cam()
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
            for emitter in self.emitters:
                emitter.update()
            # Удаляем пустые эмиттеры
            self.emitters = [e for e in self.emitters if e.get_count() > 0]
            self.update_waves(delta_time)
            self.destroy_building()
            self.drone_destruction()
            self.bullet_b()
            self.bullet_g()
            self.check_game_state()

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
            arcade.stop_sound(self.ost)
            self.ost = arcade.play_sound(random.choice([MUSIC_ATTACKS2, MUSIC_ATTACKS1, MUSIC_ATTACKS3]), volume=True)
            self.ost_UNITED = False

        if len(bugs) <= 5:
            if not self.ost_UNITED:
                arcade.stop_sound(self.ost)
                self.ost = arcade.play_sound(random.choice([MUSIC_UNITED2, MUSIC_UNITED1, MUSIC_UNITED3]), volume=True)
                self.ost_UNITED = True

    def bullet_g(self):
        for b in good_bullet:
            if b.lifetime <= 0:
                good_bullet.remove(b)
            else:
                hit_list = arcade.check_for_collision_with_list(b, bugs)
                if hit_list:
                    for i in hit_list:
                        self.create_explosion(b.center_x, b.center_y)
                        i.take_damage(b.damage)
                        self.enemies_killed += 1
                        good_bullet.remove(b)
                        arcade.play_sound(random.choice(HIT))



    def bullet_b(self):
        for b in bad_bullet:
            if b.lifetime <= 0:
                bad_bullet.remove(b)
            else:
                hit_list = arcade.check_for_collision_with_list(b, players)
                if hit_list:
                    for i in hit_list:
                        self.create_explosion(b.center_x, b.center_y)
                        i.take_damage(b.damage)
                        bad_bullet.remove(b)
                        arcade.play_sound(random.choice(HIT))
        for b in bad_bullet:
            if b.lifetime <= 0:
                bad_bullet.remove(b)
            else:
                hit_list = arcade.check_for_collision_with_list(b, buildings)
                if hit_list:
                    for i in hit_list:
                        self.create_explosion(b.center_x, b.center_y)
                        i.take_damage(b.damage)
                        bad_bullet.remove(b)
                        arcade.play_sound(random.choice(HIT))


    def create_explosion(self, x, y):
        # Основной эмиттер со звездами
        explosion_emitter = Emitter(
            center_xy=(x, y),
            emit_controller=EmitBurst(30),
            particle_factory=lambda emitter: LifetimeParticle(
                filename_or_texture=self.star_texture,
                change_xy=rand_in_circle((0, 0), 8.0),
                lifetime=random.uniform(0.01, 0.2),
                scale=random.uniform(0.1, 0.15),
                alpha=random.randint(25, 50)
            )
        )
        self.emitters.append(explosion_emitter)


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
        for emitter in self.emitters:
            emitter.draw()
        self.gui_camera.use()
        if self.game_state == 'pause':
            screen_width = self.world_camera.width
            screen_height = self.world_camera.height
            arcade.draw_lrbt_rectangle_filled(
                0, screen_width, 0, screen_height,
                (0, 0, 0, 180)
            )
            self.ui_manager.draw()

    def ui_dr(self):
        """Обновление и отрисовки UI каждый кадр с учетом камеры"""
        # Получаем размеры окна
        window = arcade.get_window()
        screen_width = window.width
        screen_height = window.height

        # Очистка SpriteList перед обновлением
        self.resource_icons.clear()

        # Вычисляем позиции относительно камеры
        camera_left = self.world_camera.bottom_left[0]
        camera_bottom = self.world_camera.bottom_left[1]

        # 1. Позиционирование таймера волны (по центру сверху экрана)
        self.wave_timer_text.x = camera_left + screen_width // 2
        self.wave_timer_text.y = camera_bottom + screen_height - 20
        self.wave_timer_text.text = str(int(self.wave_timer))
        self.wave_timer_text.draw()

        # 2. Позиционирование ресурсов (справа экрана)
        right_margin = 60
        start_y = screen_height - 60  # Отступ сверху
        vertical_spacing = 45

        # Отрисовка ресурсов только если они есть
        if self.information_about_the_building:
            resources = self.information_about_the_building

            for i, (resource_name, amount) in enumerate(resources.items()):
                # Вычисляем позицию в мировых координатах с учетом камеры
                screen_y = screen_height - 60 - i * vertical_spacing
                world_y = camera_bottom + screen_y

                # Позиция для иконки (справа)
                icon_x = camera_left + screen_width - right_margin
                icon_y = world_y

                # Позиция для текста количества (слева от иконки)
                text_x = camera_left + screen_width - right_margin - 40
                text_y = world_y

                # 1. Создание иконки ресурса
                if resource_name in TEXTYRE:
                    sprite = arcade.Sprite(TEXTYRE[resource_name])
                    sprite.center_x = icon_x
                    sprite.center_y = icon_y
                    sprite.scale = 0.25  # Масштаб 0.25
                    self.resource_icons.append(sprite)

                # 2. Обновление/создание текста количества
                if resource_name not in self.resource_count_texts:
                    self.resource_count_texts[resource_name] = arcade.Text(
                        text=str(amount),
                        x=text_x,
                        y=text_y,
                        color=arcade.color.WHITE,
                        font_size=18,
                        anchor_x="center",
                        anchor_y="center"
                    )
                else:
                    text_widget = self.resource_count_texts[resource_name]
                    text_widget.text = str(amount)
                    text_widget.x = text_x
                    text_widget.y = text_y
                    text_widget.draw()

        # Отрисовка всех иконок ресурсов
        self.resource_icons.draw()

    def pausa_dui(self):
        """Отрисовка экрана паузы с использованием UI-компонентов"""
        # Получаем размеры окна
        window = arcade.get_window()
        screen_width = self.world_camera.width
        screen_height = self.world_camera.height
        # 3. Создаем менеджер UI (если еще не создан)
        self.ui_manager = arcade.gui.UIManager()
        self.ui_manager.enable()

        # 4. Поле для ввода (чуть выше центра)
        input_field = arcade.gui.UIInputText(
            width=400,
            height=50,
            text="Имя сохранения",
            font_size=18
        )
        input_field.on_change = lambda t: self.txt(t)
        input_field.center_x = screen_width // 2
        input_field.center_y = screen_height // 2 + 150
        self.ui_manager.add(input_field)

        # 5. Кнопка "Сохранить и выйти" (по центру)
        save_button = arcade.gui.UIFlatButton(
            text="СОХРАНИТЬ И ВЫЙТИ",
            width=300,
            height=70
        )
        save_button.center_x = screen_width // 2
        save_button.center_y = screen_height // 2
        # save_button.on_click = lambda е: save_level_to_db(self.txtt, JSON, WAVES, [players, buildings,
        #                                                                  bugs, good_bullet, bad_bullet])
        self.ui_manager.add(save_button)

        # 6. Кнопка "Вернуться" (чуть ниже)
        back_button = arcade.gui.UIFlatButton(
            text="ВЕРНУТЬСЯ",
            width=300,
            height=70
        )
        back_button.center_x = screen_width // 2
        back_button.center_y = screen_height // 2 - 150
        back_button.on_click = lambda e: self.check_game_state()
        self.ui_manager.add(back_button)

    def txt(self, t):
        self.txtt = t

    def on_mouse_motion(self, x, y, dx, dy):
        if self.game_state == 'game':
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
        if self.game_state == 'game':
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
                self.buildings_built += 1
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
                        self.drones_used += 1
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
                    break

    def on_key_press(self, key: int, modifiers: int):
        self.pressed_keys.add(key)

    def on_key_release(self, key: int, modifiers: int):
        if key in self.pressed_keys:
            self.pressed_keys.remove(key)

    def check_game_state(self):
        if self.core.hp <= 0:
            self.defeat("Ядро разрушено")
        elif self.current_wave_index >= len(self.waves) and len(bugs) == 0:
            self.victory()
        elif arcade.key.ESCAPE in self.pressed_keys:
            self.game_state = "pause"
        else:
            self.game_state = "game"

    def destroy_building(self):
        for b in buildings:
            if b.hp <= 0:
                self.create_explosion_del(b.center_x, b.center_y)
                buildings.remove(b)

    def drone_destruction(self):
        for b in players:
            if b.hp <= 0:
                if b.max_hp != 3:
                    players.remove(b)
                else:
                    b.start_respawn()

    def create_explosion_del(self, x, y):
        ring_emitter = Emitter(
            center_xy=(x, y),
            emit_controller=EmitBurst(30),
            particle_factory=lambda emitter: LifetimeParticle(
                filename_or_texture=self.orb_texture,
                change_xy=rand_on_circle((0, 0), random.uniform(0.2, 4)),
                lifetime=random.uniform(0.1, 0.4),
                scale=random.uniform(0.02, 0.1),
                alpha=80
            )
        )




#Тест
def main():
    window = MyGame(555, 555, "Заводы и Тауэр Дефенс")
    arcade.run()

if __name__ == "__main__":
    main()



class GameStats:
    def __init__(self):
        self.level_results = []
        self.total_score = 0
        self.total_enemies_killed = 0
        self.total_play_time = 0.0
        self.levels_completed = 0
        self.total_buildings = 0      # новое
        self.total_drones = 0         # новое

    def add_level_result(self, level_stats):
        self.level_results.append(level_stats)
        self.total_score += level_stats.get('score', 0)
        self.total_enemies_killed += level_stats.get('enemies_killed', 0)
        self.total_play_time += level_stats.get('time_spent', 0)
        self.levels_completed += 1
        self.total_buildings += level_stats.get('buildings_built', 0)
        self.total_drones += level_stats.get('drones_used', 0)

    def get_total_stats(self):
        return {
            'total_score': self.total_score,
            'total_enemies_killed': self.total_enemies_killed,
            'total_play_time': self.total_play_time,
            'levels_completed': self.levels_completed,
            'total_buildings': self.total_buildings,
            'total_drones': self.total_drones,
            'level_results': self.level_results
        }
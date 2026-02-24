import arcade
import math
import random
from arcade.math import rand_in_circle, rand_on_circle
from arcade.particles import Emitter, EmitBurst, LifetimeParticle

from constants import (
    T_SIZE, SPRITE_SCALE, BUILDING_KEYS, BAGS,
    CAMERA_LERP, TEXTYRE,
    MUSIC_UNITED2, MUSIC_UNITED1, MUSIC_ATTACKS1, MUSIC_UNITED3,
    MUSIC_ATTACKS2, MUSIC_ATTACKS3, HIT,
    LEVELS
)
from sprite_list import good_bullet, bad_bullet, players, buildings, bugs
from core import Core
from player import Player
from buildings import ElectricDrill, BronzeFurnace, SiliconFurnace, AmmoFactory, \
    CopperTurret, BronzeTurret, LongRangeTurret
from drones import Drone
from enemies import Beetle, ArmoredBeetle, SpittingBeetle, DominicTorettoBeetle, HarkerBeetle
from menu import LevelCompleteView, GameOverView, FinalResultsView


class GameView(arcade.View):
    """Основной игровой процесс"""

    def __init__(self, level_number: int, user_id: int, username: str):
        super().__init__()
        self.current_level = level_number
        self.user_id = user_id
        self.username = username

        level_data = LEVELS.get(self.current_level)
        if level_data is None:
            print(f"Ошибка: уровень {self.current_level} не найден. Используется уровень 1.")
            level_data = LEVELS[1]
            self.current_level = 1

        self.waves = level_data["waves"]
        self.map_json = level_data["map"]

        # Камеры
        self.world_camera = arcade.camera.Camera2D()
        self.gui_camera = arcade.camera.Camera2D()
        self.cam_target = (0, 0)

        # Волны
        self.current_wave_index = 0
        self.wave_timer = 100

        # Состояние
        self.game_state = "game"
        self.pressed_keys = set()
        self.grid = None

        self.player = None
        self.core = None
        self.rote_dron = False
        self.information_about_the_building = {}

        # Карта
        self.map_height_pixels = None
        self.map_width_pixels = None
        self.map_height = None
        self.map_width = None
        self.map = None

        # Спрайты и эффекты
        self.buildings = arcade.SpriteList()
        self.bullets = arcade.SpriteList()
        self.bugs = arcade.SpriteList()
        self.drones = arcade.SpriteList()
        self.resource_icons = arcade.SpriteList()
        self.emitters = []

        self.star_texture = arcade.load_texture("Изображения/Остальное/Пуля.png")
        self.orb_texture = arcade.load_texture("Изображения/Остальное/Камень.png")

        self.wave_timer_text = None
        self.resource_textures = {}
        self.resource_count_texts = {}
        self.ost = None
        self.ost_UNITED = True

    def on_show_view(self):
        arcade.set_background_color(arcade.color.BLACK)
        self.setup()
        self.load_map()
        self.pausa_dui()

    def on_hide_view(self):
        # Очищаем глобальные списки спрайтов, чтобы не оставались в памяти
        players.clear()
        buildings.clear()
        bugs.clear()
        good_bullet.clear()
        bad_bullet.clear()
        if self.ost:
            arcade.stop_sound(self.ost)

    def load_map(self):
        self.map = arcade.load_tilemap(self.map_json, scaling=SPRITE_SCALE)
        self.map_width = self.map.width
        self.map_height = self.map.height
        self.map_width_pixels = self.map_width * T_SIZE
        self.map_height_pixels = self.map_height * T_SIZE

    def setup_ui(self):
        window = self.window
        self.wave_timer_text = arcade.Text(
            text="0",
            x=window.width // 2,
            y=window.height - 20,
            color=arcade.color.WHITE,
            font_size=24,
            anchor_x="center",
            anchor_y="top"
        )

    def setup(self):
        self.core = Core(SPRITE_SCALE, 520, 520)
        buildings.append(self.core)
        self.player = Player("Изображения/Остальное/Нгг.png", SPRITE_SCALE, self.core)
        players.append(self.player)
        self.ost = arcade.play_sound(random.choice([MUSIC_UNITED2, MUSIC_UNITED1, MUSIC_UNITED3]))
        self.ost_UNITED = True
        self.setup_ui()

    def cam(self):
        cam_x, cam_y = self.world_camera.position
        px, py = self.player.center_x, self.player.center_y

        target_x, target_y = px, py

        half_w = self.world_camera.viewport_width / 2
        min_x = half_w
        max_x = self.map_width_pixels - half_w
        target_x = max(min_x, min(max_x, target_x))

        half_h = self.world_camera.viewport_height / 2
        min_y = half_h
        max_y = self.map_height_pixels - half_h
        target_y = max(min_y, min(max_y, target_y))

        smooth_x = (1 - CAMERA_LERP) * cam_x + CAMERA_LERP * target_x
        smooth_y = (1 - CAMERA_LERP) * cam_y + CAMERA_LERP * target_y

        self.world_camera.position = (smooth_x, smooth_y)

    def on_update(self, delta_time: float):
        if self.game_state == 'game':
            self.cam()
            if players:
                self.player.handle_movement(delta_time, self.pressed_keys)
                self.player.update(delta_time)

                self.player.center_x = max(T_SIZE // 2, min(self.map_width_pixels - T_SIZE // 2, self.player.center_x))
                self.player.center_y = max(T_SIZE // 2, min(self.map_height_pixels - T_SIZE // 2, self.player.center_y))

            for emitter in self.emitters:
                emitter.update()
            self.emitters = [e for e in self.emitters if e.get_count() > 0]
            self.update_waves(delta_time)
            for bug in bugs:
                bug.update(delta_time)
            self.destroy_building()
            self.drone_destruction()
            self.bullet_b()
            self.bullet_g()
            self.check_game_state()

    def update_waves(self, delta_time: float):
        self.wave_timer -= delta_time

        for bug in bugs:
            if bug.hp <= 0:
                bugs.remove(bug)

        if self.wave_timer <= 0:
            if self.current_wave_index < len(self.waves):
                for bug_name in self.waves[self.current_wave_index]:
                    if random.randint(0, 1):
                        x = random.randint(0, self.map_width_pixels)
                        y = 0
                    else:
                        y = random.randint(0, self.map_height_pixels)
                        x = 0
                    bug_class = BAGS.get(bug_name)
                    if bug_class:
                        bugs.append(bug_class(x, y, self.core))
                self.current_wave_index += 1
                self.wave_timer = 100
                if self.ost:
                    arcade.stop_sound(self.ost)
                self.ost = arcade.play_sound(random.choice([MUSIC_ATTACKS2, MUSIC_ATTACKS1, MUSIC_ATTACKS3]), volume=True)
                self.ost_UNITED = False

        if len(bugs) <= 5:
            if not self.ost_UNITED:
                if self.ost:
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
        self.clear()
        self.world_camera.use()
        if self.map:
            for layer_name, layer in self.map.sprite_lists.items():
                layer.draw()
        self.ui_dr()
        buildings.draw()
        bugs.draw()
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
        window = self.window
        screen_width = window.width
        screen_height = window.height

        camera_left = self.world_camera.bottom_left[0]
        camera_bottom = self.world_camera.bottom_left[1]

        # ОЧИСТКА СПРАЙТОВ РЕСУРСОВ КАЖДЫЙ КАДР - ЭТО ГЛАВНОЕ ИЗМЕНЕНИЕ!
        self.resource_icons.clear()

        # Обновление таймера волны
        self.wave_timer_text.x = camera_left + screen_width // 2
        self.wave_timer_text.y = camera_bottom + screen_height - 20
        self.wave_timer_text.text = str(int(self.wave_timer))
        self.wave_timer_text.draw()

        right_margin = 60
        vertical_spacing = 45

        # Очистка старых текстовых элементов
        self.resource_count_texts.clear()

        if self.information_about_the_building:
            resources = self.information_about_the_building
            for i, (resource_name, amount) in enumerate(resources.items()):
                screen_y = screen_height - 60 - i * vertical_spacing
                world_y = camera_bottom + screen_y

                icon_x = camera_left + screen_width - right_margin
                icon_y = world_y
                text_x = camera_left + screen_width - right_margin - 40
                text_y = world_y

                if resource_name in TEXTYRE:
                    sprite = arcade.Sprite(TEXTYRE[resource_name])
                    sprite.center_x = icon_x
                    sprite.center_y = icon_y
                    sprite.scale = 0.25
                    self.resource_icons.append(sprite)

                # Создаем новый текстовый элемент для каждого ресурса
                text_widget = arcade.Text(
                    text=str(amount),
                    x=text_x,
                    y=text_y,
                    color=arcade.color.WHITE,
                    font_size=18,
                    anchor_x="center",
                    anchor_y="center"
                )
                text_widget.draw()

        self.resource_icons.draw()

    def pausa_dui(self):
        screen_width = self.window.width
        screen_height = self.window.height
        self.ui_manager = arcade.gui.UIManager()

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

        save_button = arcade.gui.UIFlatButton(
            text="СОХРАНИТЬ И ВЫЙТИ",
            width=300,
            height=70
        )
        save_button.center_x = screen_width // 2
        save_button.center_y = screen_height // 2
        self.ui_manager.add(save_button)

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
                    self.information_about_the_building = i.get_all()
                    return
            self.information_about_the_building = {}

    def on_mouse_press(self, x: float, y: float, button: int, modifiers: int):
        if self.game_state == 'game':
            if arcade.MOUSE_BUTTON_LEFT == button:
                self.build_building(x, y)
            elif arcade.MOUSE_BUTTON_RIGHT == button:
                self.f_rote_dron(x, y)
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

            if arcade.key.DELETE == i:
                for u in buildings:
                    if u.max_hp != 20:
                        if u.center_x == x3 and u.center_y == y3:
                            buildings.remove(u)
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
                    if not self.rote_dron:
                        if self.core.has("Кремний", 1) and self.core.has("Медь", 5) and self.core.has("Олово", 3):
                            self.core.remove("Кремний", 1)
                            self.core.remove("Олово", 3)
                            self.core.remove("Медь", 5)
                            players.append(Drone(self.rote_dron.append(t)))
                            self.rote_dron = False
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
            self.game_state = "game_over"
            self.show_game_over("Ядро разрушено")
        elif self.current_wave_index >= len(self.waves) and len(bugs) == 0:
            self.game_state = "victory"
            self.show_victory()
        elif arcade.key.ESCAPE in self.pressed_keys:
            self.game_state = "pause"
            self.ui_manager.enable()
        else:
            self.game_state = "game"
            self.ui_manager.disable()

    def show_game_over(self, reason):
        stats = {
            'score': 0,
            'enemies_killed': 0,
            'time_survived': 0,
            'waves_completed': self.current_wave_index,
        }
        game_over_view = GameOverView(
            level_number=self.current_level,
            reason=reason,
            stats=stats,
            user_id=self.user_id,
            callback=self.handle_game_over
        )
        self.window.show_view(game_over_view)

    def show_victory(self):
        level_data = {
            'level_number': self.current_level,
            'score': 1000,  # Здесь надо посчитать реальные очки
            'enemies_killed': 0,
            'time_spent': 0,
            'waves_completed': len(self.waves),
            'resources_collected': 0,
            'buildings_built': 0,
            'drones_used': 0,
        }
        if self.current_level >= 3:
            final_view = FinalResultsView(
                total_stats={
                    'total_score': 0,
                    'total_enemies_killed': 0,
                    'total_play_time': 0,
                    'levels_completed': self.current_level,
                },
                user_id=self.user_id,
                username=self.username,
                callback=self.handle_final
            )
            self.window.show_view(final_view)
        else:
            complete_view = LevelCompleteView(
                level_data=level_data,
                user_id=self.user_id,
                username=self.username,
                callback=self.handle_level_complete
            )
            self.window.show_view(complete_view)

    def handle_level_complete(self, action):
        if action == 'next_level':
            next_level = self.current_level + 1
            game_view = GameView(next_level, self.user_id, self.username)
            self.window.show_view(game_view)
        elif action == 'retry_level':
            game_view = GameView(self.current_level, self.user_id, self.username)
            self.window.show_view(game_view)
        elif action == 'to_menu':
            self.return_to_menu()

    def handle_game_over(self, action):
        if action == 'retry_level':
            game_view = GameView(self.current_level, self.user_id, self.username)
            self.window.show_view(game_view)
        elif action == 'to_menu':
            self.return_to_menu()

    def handle_final(self, action):
        if action == 'new_game':
            game_view = GameView(1, self.user_id, self.username)
            self.window.show_view(game_view)
        elif action == 'to_menu':
            self.return_to_menu()

    def return_to_menu(self):
        from menu import StartMenuView
        menu_view = StartMenuView()
        self.window.show_view(menu_view)

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
        self.emitters.append(ring_emitter)
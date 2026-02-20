# game.py
import arcade
from arcade.gui import UIManager
import math
import random

from arcade.math import rand_in_circle, rand_on_circle
from arcade.particles import Emitter, EmitBurst, LifetimeParticle

from constants import (
    T_SIZE, SPRITE_SCALE, BUILDING_HP, BUILDING_KEYS, BAGS,
    CAMERA_LERP, RESOURCES, TEXTYRE,
    MUSIC_MENU, MUSIC_UNITED2, MUSIC_UNITED1, MUSIC_ATTACKS1, MUSIC_UNITED3,
    MUSIC_ATTACKS2, MUSIC_ATTACKS3, HIT,
    LEVELS, CURRENT_LEVEL   # импортируем данные уровней и номер по умолчанию
)
from sprite_list import good_bullet, bad_bullet, players, buildings, bugs
from core import Core
from player import Player
from buildings import (Building, ElectricDrill,
                       BronzeFurnace, SiliconFurnace, AmmoFactory,
                       CopperTurret, BronzeTurret, LongRangeTurret)
from drones import Drone
from enemies import (Bug, Beetle, ArmoredBeetle, SpittingBeetle,
                     DominicTorettoBeetle, HarkerBeetle)


class MyGame(arcade.Window):
    """Основной класс игры - управляет всем игровым процессом"""

    def __init__(self, width: int, height: int, title: str, level_number: int = None):
        super().__init__(width, height, title)

        # Определяем номер текущего уровня (из параметра или константы)
        self.current_level = level_number if level_number is not None else CURRENT_LEVEL

        # Загружаем данные уровня из словаря LEVELS
        level_data = LEVELS.get(self.current_level)
        if level_data is None:
            print(f"Ошибка: данные для уровня {self.current_level} не найдены. Используется уровень 1.")
            level_data = LEVELS[1]
            self.current_level = 1

        self.waves = level_data["waves"]          # список волн
        self.map_json = level_data["map"]         # имя файла карты

        # Инициализация камер и т.п.
        self.txtt = None
        self.world_camera = arcade.camera.Camera2D()
        self.gui_camera = arcade.camera.Camera2D()
        self.cam_target = (0, 0)

        # Система волн
        self.current_wave_index = 0
        self.wave_timer = 100

        # Состояние игры
        self.game_state = "game"
        self.pressed_keys = set()
        self.grid = None

        self.player = None
        self.core = None
        self.rote_dron = False
        self.information_about_the_building = {}

        # Параметры карты (будут установлены в load_map)
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
        self.star_texture = arcade.load_texture("Изображения/Остальное/Пуля.png")
        self.orb_texture = arcade.load_texture("Изображения/Остальное/Камень.png")
        self.pausa_dui()

    def load_map(self):
        """
        Загрузка карты из файла, указанного в self.map_json.
        """
        try:
            self.map = arcade.load_tilemap(self.map_json)
        except Exception as e:
            print(f"Не удалось загрузить карту {self.map_json}: {e}. Используется тестовая карта.")
            self.map = arcade.load_tilemap(":resources:/tiled_maps/level_1.json")

        self.map_width = self.map.width
        self.map_height = self.map.height
        self.map_width_pixels = self.map_width * T_SIZE
        self.map_height_pixels = self.map_height * T_SIZE

    def setup_ui(self):
        window = arcade.get_window()
        self.wave_timer_text = arcade.Text(
            text="0",
            x=window.width // 2,
            y=window.height - 20,
            color=arcade.color.WHITE,
            font_size=24,
            anchor_x="center",
            anchor_y="top"
        )
        self.resource_textures = {}
        self.resource_count_texts = {}

    def setup(self):
        self.core = Core(SPRITE_SCALE, 200, 200)
        buildings.append(self.core)
        self.player = Player("Изображения/Остальное/Нгг.png", SPRITE_SCALE, self.core)
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

        half_w = int(self.world_camera.viewport_width / 2)
        half_h = int(self.world_camera.viewport_height / 2)
        target_x = max(half_w, min(int(self.map_width_pixels) - half_w, target_x))
        target_y = max(half_h, min(int(self.map_height_pixels) - half_h, target_y))

        smooth_x = (1 - CAMERA_LERP) * cam_x + CAMERA_LERP * target_x
        smooth_y = (1 - CAMERA_LERP) * cam_y + CAMERA_LERP * target_y
        self.cam_target = (smooth_x, smooth_y)

        self.world_camera.position = (self.cam_target[0], self.cam_target[1])

    def on_update(self, delta_time: float):
        if self.game_state == 'game':
            self.cam()
            if players:
                self.player.handle_movement(delta_time, self.pressed_keys)
                self.player.update(delta_time)

            position = (self.player.center_x, self.player.center_y)
            self.world_camera.position = arcade.math.lerp_2d(
                self.world_camera.position,
                position,
                0.5,
            )
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
                    # Спавн врага
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
                arcade.stop_sound(self.ost)
                self.ost = arcade.play_sound(random.choice([MUSIC_ATTACKS2, MUSIC_ATTACKS1, MUSIC_ATTACKS3]), volume=True)
                self.ost_UNITED = False
            else:
                # Волны закончились, просто ждём
                pass

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
        window = arcade.get_window()
        screen_width = window.width
        screen_height = window.height

        camera_left = self.world_camera.bottom_left[0]
        camera_bottom = self.world_camera.bottom_left[1]

        self.wave_timer_text.x = camera_left + screen_width // 2
        self.wave_timer_text.y = camera_bottom + screen_height - 20
        self.wave_timer_text.text = str(int(self.wave_timer))
        self.wave_timer_text.draw()

        right_margin = 60
        start_y = screen_height - 60
        vertical_spacing = 45

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

        self.resource_icons.draw()

    def pausa_dui(self):
        window = arcade.get_window()
        screen_width = self.world_camera.width
        screen_height = self.world_camera.height
        self.ui_manager = arcade.gui.UIManager()
        self.ui_manager.enable()

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
        # save_button.on_click = lambda е: save_level_to_db(self.txtt, ...)
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
                    self.information_about_the_building = i.resources
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
                            # возврат ресурсов (упрощённо)
                            # for res in u.cost.cost:  # нужно адаптировать под ResourceTransaction
                            #     u.cost.cost[res] = int(u.cost.cost[res] / 2)
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
                        # self.core.add_resource("Кремний", -3) и т.д. (нужно реализовать)
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
                    # self.core.add_resource("Кремний", 2) и т.д.
                    break

    def on_key_press(self, key: int, modifiers: int):
        self.pressed_keys.add(key)

    def on_key_release(self, key: int, modifiers: int):
        if key in self.pressed_keys:
            self.pressed_keys.remove(key)

    def check_game_state(self):
        if self.core.hp <= 0:
            self.game_state = "game_over"
        elif self.current_wave_index >= len(self.waves) and len(bugs) == 0:
            self.game_state = "victory"
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
        self.emitters.append(ring_emitter)


def main():
    window = MyGame(555, 555, "Заводы и Тауэр Дефенс")
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
        self.level_results.append(level_stats)
        self.total_score += level_stats.get('score', 0)
        self.total_enemies_killed += level_stats.get('enemies_killed', 0)
        self.total_play_time += level_stats.get('time_spent', 0)
        self.levels_completed += 1

    def get_total_stats(self):
        return {
            'total_score': self.total_score,
            'total_enemies_killed': self.total_enemies_killed,
            'total_play_time': self.total_play_time,
            'levels_completed': self.levels_completed,
            'level_results': self.level_results
        }
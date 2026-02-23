import arcade
import random
import sqlite3
from arcade.gui import UIManager, UIBoxLayout, UIFlatButton, UILabel, UIInputText
from typing import Dict, List, Tuple, Optional, Any, Callable
from datetime import datetime

from database import GameDatabase
from constants import MUSIC_MENU


class StartMenuView(arcade.View):
    """Стартовое меню с авторизацией и выбором уровня"""

    def __init__(self):
        super().__init__()
        self.ui_manager = UIManager()
        self.db = GameDatabase()
        self.current_user = None
        self.current_user_id = None
        self.ost = None
        self.stars = []
        self.setup_ui()

    def on_show_view(self):
        arcade.set_background_color(arcade.color.DARK_SLATE_BLUE)
        self.ui_manager.enable()
        if MUSIC_MENU:
            self.ost = arcade.play_sound(MUSIC_MENU, volume=True)

    def on_hide_view(self):
        self.ui_manager.disable()
        if self.ost:
            arcade.stop_sound(self.ost)

    def setup_ui(self):
        self.ui_manager.clear()
        font_name = "Courier New"
        button_style = {
            "normal": UIFlatButton.UIStyle(
                font_name=font_name, font_size=14, font_color=arcade.color.WHITE, bg=(80, 80, 80)
            ),
            "hover": UIFlatButton.UIStyle(
                font_name=font_name, font_size=14, font_color=arcade.color.WHITE, bg=(100, 100, 100)
            ),
            "press": UIFlatButton.UIStyle(
                font_name=font_name, font_size=14, font_color=arcade.color.WHITE, bg=(60, 60, 60)
            ),
            "disabled": UIFlatButton.UIStyle(
                font_name=font_name, font_size=14, font_color=arcade.color.GRAY, bg=(40, 40, 40)
            )
        }

        v_box = UIBoxLayout(vertical=True, space_between=20)

        v_box.add(UILabel(text="", width=self.window.width, height=100))
        title_label = UILabel(
            text="🚀 ЗАВОДЫ И ТАУЭР ДЕФЕНС 🚀",
            font_size=36, font_name=font_name, text_color=arcade.color.GOLD,
            width=self.window.width - 100, align="center"
        )
        v_box.add(title_label)

        subtitle_label = UILabel(
            text="Защити ядро, строй заводы, управляй дронами!",
            font_size=18, font_name=font_name, text_color=arcade.color.LIGHT_GRAY,
            width=self.window.width - 100, align="center"
        )
        v_box.add(subtitle_label)
        v_box.add(UILabel(text="", height=30))

        # Авторизация
        auth_container = UIBoxLayout(vertical=True, space_between=10)
        auth_label = UILabel(
            text="Введите имя игрока:",
            font_size=20, font_name=font_name, text_color=arcade.color.LIGHT_BLUE,
            width=300, align="center"
        )
        auth_container.add(auth_label)

        self.username_input = UIInputText(
            width=300, height=40, font_size=18, font_name=font_name, text_color=arcade.color.BLACK
        )
        auth_container.add(self.username_input)

        login_button = UIFlatButton(text="Войти", width=300, height=40, style=button_style)

        @login_button.event("on_click")
        def on_login(event):
            username = self.username_input.text.strip()
            if username:
                self.login_user(username)

        auth_container.add(login_button)

        auth_centered = UIBoxLayout(vertical=False)
        auth_centered.add(UILabel(text="", width=(self.window.width - 300) // 2))
        auth_centered.add(auth_container)
        auth_centered.add(UILabel(text="", width=(self.window.width - 300) // 2))
        v_box.add(auth_centered)

        # Контейнер для выбора уровня (появится после входа)
        self.level_container = UIBoxLayout(vertical=True, space_between=10)
        v_box.add(self.level_container)

        # Кнопка выхода
        exit_centered = UIBoxLayout(vertical=False)
        exit_centered.add(UILabel(text="", width=(self.window.width - 200) // 2))
        exit_button = UIFlatButton(text="Выход", width=200, height=40, style=button_style)

        @exit_button.event("on_click")
        def on_exit(event):
            arcade.exit()

        exit_centered.add(exit_button)
        exit_centered.add(UILabel(text="", width=(self.window.width - 200) // 2))
        v_box.add(exit_centered)

        self.ui_manager.add(v_box)

    def login_user(self, username: str):
        self.current_user_id = self.db.register_user(username)
        if self.current_user_id > 0:
            self.current_user = username
            self.show_level_selection()

    def show_level_selection(self):
        self.level_container.clear()
        user_stats = self.db.get_user_stats(self.current_user_id)
        unlocked_levels = user_stats.get('unlocked_levels', 1)

        title_label = UILabel(
            text=f"Добро пожаловать, {self.current_user}!",
            font_size=24, font_name="Courier New", text_color=arcade.color.LIGHT_GREEN,
            width=self.window.width - 100, align="center"
        )
        self.level_container.add(title_label)

        level_button_style = {
            "normal": UIFlatButton.UIStyle(
                font_name="Courier New", font_size=14, font_color=arcade.color.WHITE, bg=(80, 80, 80)
            ),
            "hover": UIFlatButton.UIStyle(
                font_name="Courier New", font_size=14, font_color=arcade.color.WHITE, bg=(100, 100, 100)
            ),
            "press": UIFlatButton.UIStyle(
                font_name="Courier New", font_size=14, font_color=arcade.color.WHITE, bg=(60, 60, 60)
            ),
            "disabled": UIFlatButton.UIStyle(
                font_name="Courier New", font_size=14, font_color=arcade.color.GRAY, bg=(40, 40, 40)
            )
        }

        total_levels = 3
        for level in range(1, total_levels + 1):
            level_centered = UIBoxLayout(vertical=False)
            level_centered.add(UILabel(text="", width=(self.window.width - 250) // 2))

            icon = "🔓" if level <= unlocked_levels else "🔒"
            level_button = UIFlatButton(
                text=f"{icon} Уровень {level}",
                width=200, height=50, style=level_button_style
            )

            if level <= unlocked_levels:
                @level_button.event("on_click")
                def on_level_click(event, lvl=level):
                    self.start_level(lvl)

            level_centered.add(level_button)

            # Показываем рекорд
            level_records = self.db.get_user_level_records(self.current_user_id)
            record = level_records.get(level, {})
            if record:
                record_label = UILabel(
                    text=f"🏆 {record.get('score', 0)}",
                    font_size=14, font_name="Courier New", text_color=arcade.color.GOLD,
                    width=50, align="center"
                )
                level_centered.add(record_label)
            else:
                level_centered.add(UILabel(text="", width=50))

            level_centered.add(UILabel(text="", width=(self.window.width - 250) // 2))
            self.level_container.add(level_centered)

        # Кнопка продолжения (если есть сохранение)
        saved_state = self.db.load_game_state(self.current_user_id)
        if saved_state:
            continue_centered = UIBoxLayout(vertical=False)
            continue_centered.add(UILabel(text="", width=(self.window.width - 250) // 2))
            continue_button = UIFlatButton(
                text="🎮 Продолжить игру",
                width=250, height=50, style=level_button_style
            )
            @continue_button.event("on_click")
            def on_continue(event):
                self.continue_game()
            continue_centered.add(continue_button)
            continue_centered.add(UILabel(text="", width=(self.window.width - 250) // 2))
            self.level_container.add(continue_centered)

    def start_level(self, level_number: int):
        from game import GameView
        game_view = GameView(level_number, self.current_user_id, self.current_user)
        self.window.show_view(game_view)

    def continue_game(self):
        saved_state = self.db.load_game_state(self.current_user_id)
        if saved_state:
            level = saved_state.get('current_level', 1)
            self.start_level(level)

    def on_update(self, delta_time: float):
        if not self.stars:
            for _ in range(100):
                self.stars.append({
                    'x': random.randint(0, self.window.width),
                    'y': random.randint(0, self.window.height),
                    'size': random.uniform(0.5, 3.0),
                    'speed': random.uniform(0.1, 0.5),
                    'brightness': random.uniform(0.3, 1.0)
                })
        for star in self.stars:
            star['y'] += star['speed']
            if star['y'] > self.window.height:
                star['y'] = 0
                star['x'] = random.randint(0, self.window.width)

    def on_draw(self):
        self.clear()
        for star in self.stars:
            brightness = int(255 * star['brightness'])
            arcade.draw_circle_filled(star['x'], star['y'], star['size'],
                                       (brightness, brightness, brightness))
        self.ui_manager.draw()

        if self.current_user:
            stats = self.db.get_user_stats(self.current_user_id)
            arcade.draw_text(
                f"Игрок: {self.current_user}",
                10, self.window.height - 30,
                arcade.color.LIGHT_GRAY, 14, font_name="Courier New"
            )
            arcade.draw_text(
                f"Уровней пройдено: {stats.get('unlocked_levels', 1)}",
                10, self.window.height - 50,
                arcade.color.LIGHT_GRAY, 12, font_name="Courier New"
            )

    def on_close(self):
        self.db.close()


class LevelCompleteView(arcade.View):
    """Окно успешного завершения уровня"""

    def __init__(self, level_data: Dict[str, Any], user_id: int, username: str, callback: Callable):
        super().__init__()
        self.level_data = level_data
        self.user_id = user_id
        self.username = username
        self.callback = callback
        self.db = GameDatabase()
        self.ui_manager = UIManager()
        self.setup_ui()

    def on_show_view(self):
        arcade.set_background_color(arcade.color.DARK_GREEN)
        self.ui_manager.enable()

    def on_hide_view(self):
        self.ui_manager.disable()
        self.db.close()

    def setup_ui(self):
        main_box = UIBoxLayout(vertical=True, space_between=15)
        main_box.add(UILabel(text="", height=50))

        title_label = UILabel(
            text="🎉 УРОВЕНЬ ПРОЙДЕН! 🎉",
            font_size=36, font_name="Courier New", text_color=arcade.color.GOLD,
            width=self.window.width - 100, align="center"
        )
        main_box.add(title_label)

        level_info = UILabel(
            text=f"Уровень {self.level_data.get('level_number', 1)}",
            font_size=24, text_color=arcade.color.LIGHT_GREEN,
            width=self.window.width - 100, align="center"
        )
        main_box.add(level_info)
        main_box.add(UILabel(text="", height=20))

        stats = [
            (f"🏆 Очки: {self.level_data.get('score', 0)}", arcade.color.GOLD),
            (f"🎯 Убито врагов: {self.level_data.get('enemies_killed', 0)}", arcade.color.RED),
            (f"⏱️ Время: {self.level_data.get('time_spent', 0):.1f} сек", arcade.color.CYAN),
            (f"🌊 Волн пройдено: {self.level_data.get('waves_completed', 0)}", arcade.color.BLUE),
            (f"🏭 Построено зданий: {self.level_data.get('buildings_built', 0)}", arcade.color.BROWN),
            (f"🚁 Использовано дронов: {self.level_data.get('drones_used', 0)}", arcade.color.SILVER)
        ]
        for text, color in stats:
            centered = UIBoxLayout(vertical=False)
            centered.add(UILabel(text="", width=(self.window.width - 400) // 2))
            centered.add(UILabel(text=text, font_size=18, text_color=color, width=400, align="center"))
            centered.add(UILabel(text="", width=(self.window.width - 400) // 2))
            main_box.add(centered)

        main_box.add(UILabel(text="", height=40))

        # Кнопки
        buttons_container = UIBoxLayout(vertical=False, space_between=20)
        left_spacer = UIBoxLayout(vertical=True)
        left_spacer.add(UILabel(text="", width=(self.window.width - 640) // 2, height=50))
        buttons_container.add(left_spacer)

        current_level = self.level_data.get('level_number', 1)
        is_last = current_level >= 3

        if not is_last:
            next_button = UIFlatButton(text="▶ Следующий уровень", width=200, height=50)
            @next_button.event("on_click")
            def on_next(event):
                self.callback('next_level')
            buttons_container.add(next_button)

        retry_button = UIFlatButton(text="🔄 Повторить", width=200 if is_last else 200, height=50)
        @retry_button.event("on_click")
        def on_retry(event):
            self.callback('retry_level')
        buttons_container.add(retry_button)

        menu_button = UIFlatButton(text="🏠 В меню", width=200, height=50)
        @menu_button.event("on_click")
        def on_menu(event):
            self.callback('to_menu')
        buttons_container.add(menu_button)

        right_spacer = UIBoxLayout(vertical=True)
        right_spacer.add(UILabel(text="", width=(self.window.width - 640) // 2, height=50))
        buttons_container.add(right_spacer)

        main_box.add(buttons_container)
        self.ui_manager.add(main_box)

        if self.user_id:
            self.db.save_level_record(self.user_id, self.level_data)

    def on_draw(self):
        self.clear()
        for _ in range(50):
            x = random.randint(0, self.window.width)
            y = random.randint(0, self.window.height)
            color = random.choice([arcade.color.GOLD, arcade.color.RED, arcade.color.GREEN])
            arcade.draw_circle_filled(x, y, 2, color)
        self.ui_manager.draw()


class GameOverView(arcade.View):
    """Окно поражения"""

    def __init__(self, level_number: int, reason: str, stats: Dict[str, Any],
                 user_id: int, callback: Callable):
        super().__init__()
        self.level_number = level_number
        self.reason = reason
        self.stats = stats
        self.user_id = user_id
        self.callback = callback
        self.db = GameDatabase()
        self.ui_manager = UIManager()
        self.setup_ui()

    def on_show_view(self):
        arcade.set_background_color(arcade.color.DARK_RED)
        self.ui_manager.enable()

    def on_hide_view(self):
        self.ui_manager.disable()
        self.db.close()

    def setup_ui(self):
        main_box = UIBoxLayout(vertical=True, space_between=15)
        main_box.add(UILabel(text="", height=80))

        title_label = UILabel(
            text="💀 ПОРАЖЕНИЕ 💀",
            font_size=36, font_name="Courier New", text_color=arcade.color.BLACK,
            width=self.window.width - 100, align="center"
        )
        main_box.add(title_label)

        reason_label = UILabel(
            text=f"Причина: {self.reason}",
            font_size=24, text_color=arcade.color.WHITE,
            width=self.window.width - 100, align="center"
        )
        main_box.add(reason_label)

        level_label = UILabel(
            text=f"Уровень {self.level_number}",
            font_size=20, text_color=arcade.color.LIGHT_GRAY,
            width=self.window.width - 100, align="center"
        )
        main_box.add(level_label)
        main_box.add(UILabel(text="", height=30))

        if self.stats:
            progress_label = UILabel(
                text="Достигнутый прогресс:",
                font_size=20, text_color=arcade.color.LIGHT_YELLOW,
                width=self.window.width - 100, align="center"
            )
            main_box.add(progress_label)

            for text, color in [
                (f"🏆 Очки: {self.stats.get('score', 0)}", arcade.color.GOLD),
                (f"🎯 Убито врагов: {self.stats.get('enemies_killed', 0)}", arcade.color.RED),
                (f"⏱️ Время: {self.stats.get('time_survived', 0):.1f} сек", arcade.color.CYAN),
                (f"🌊 Волн пройдено: {self.stats.get('waves_completed', 0)}", arcade.color.BLUE)
            ]:
                centered = UIBoxLayout(vertical=False)
                centered.add(UILabel(text="", width=(self.window.width - 400) // 2))
                centered.add(UILabel(text=text, font_size=16, text_color=color, width=400, align="center"))
                centered.add(UILabel(text="", width=(self.window.width - 400) // 2))
                main_box.add(centered)

        main_box.add(UILabel(text="", height=50))

        # Кнопки
        buttons_container = UIBoxLayout(vertical=False, space_between=20)
        left_spacer = UIBoxLayout(vertical=True)
        left_spacer.add(UILabel(text="", width=(self.window.width - 440) // 2, height=50))
        buttons_container.add(left_spacer)

        retry_button = UIFlatButton(text="🔄 Повторить уровень", width=200, height=50)
        @retry_button.event("on_click")
        def on_retry(event):
            self.callback('retry_level')
        buttons_container.add(retry_button)

        menu_button = UIFlatButton(text="🏠 В главное меню", width=200, height=50)
        @menu_button.event("on_click")
        def on_menu(event):
            self.callback('to_menu')
        buttons_container.add(menu_button)

        right_spacer = UIBoxLayout(vertical=True)
        right_spacer.add(UILabel(text="", width=(self.window.width - 440) // 2, height=50))
        buttons_container.add(right_spacer)

        main_box.add(buttons_container)
        self.ui_manager.add(main_box)

    def on_draw(self):
        self.clear()
        # Имитация трещин
        arcade.draw_line(100, 100, 700, 500, arcade.color.BLACK, 3)
        arcade.draw_line(200, 500, 600, 200, arcade.color.BLACK, 3)
        arcade.draw_line(400, 100, 400, 500, arcade.color.BLACK, 2)
        self.ui_manager.draw()


class FinalResultsView(arcade.View):
    """Финальное окно после прохождения всех уровней"""

    def __init__(self, total_stats: Dict[str, Any], user_id: int, username: str, callback: Callable):
        super().__init__()
        self.total_stats = total_stats
        self.user_id = user_id
        self.username = username
        self.callback = callback
        self.db = GameDatabase()
        self.ui_manager = UIManager()
        self.setup_ui()

    def on_show_view(self):
        arcade.set_background_color(arcade.color.DARK_BLUE)
        self.ui_manager.enable()

    def on_hide_view(self):
        self.ui_manager.disable()
        self.db.close()

    def setup_ui(self):
        main_box = UIBoxLayout(vertical=True, space_between=10)
        main_box.add(UILabel(text="", height=30))

        title_label = UILabel(
            text="🏆 ИГРА ПРОЙДЕНА! 🏆",
            font_size=36, font_name="Courier New", text_color=arcade.color.GOLD,
            width=self.window.width - 100, align="center"
        )
        main_box.add(title_label)

        congrats_label = UILabel(
            text=f"Поздравляем, {self.username}!",
            font_size=24, text_color=arcade.color.LIGHT_GREEN,
            width=self.window.width - 100, align="center"
        )
        main_box.add(congrats_label)

        subtitle_label = UILabel(
            text="Вы прошли все 3 уровня игры!",
            font_size=20, text_color=arcade.color.LIGHT_BLUE,
            width=self.window.width - 100, align="center"
        )
        main_box.add(subtitle_label)
        main_box.add(UILabel(text="", height=20))

        total_label = UILabel(
            text="📊 ОБЩАЯ СТАТИСТИКА:",
            font_size=22, text_color=arcade.color.LIGHT_BLUE,
            width=self.window.width - 100, align="center"
        )
        main_box.add(total_label)

        stats = [
            (f"🏆 Общий счет: {self.total_stats.get('total_score', 0)}", arcade.color.GOLD),
            (f"🎯 Всего врагов убито: {self.total_stats.get('total_enemies_killed', 0)}", arcade.color.RED),
            (f"⏱️ Общее время игры: {self.total_stats.get('total_play_time', 0):.1f} сек", arcade.color.CYAN),
            (f"🌊 Всего уровней пройдено: {self.total_stats.get('levels_completed', 0)}/3", arcade.color.BLUE),
            (f"🏭 Всего построено зданий: {self.total_stats.get('total_buildings', 0)}", arcade.color.BROWN),
            (f"🚁 Использовано дронов: {self.total_stats.get('total_drones', 0)}", arcade.color.SILVER)
        ]
        for text, color in stats:
            centered = UIBoxLayout(vertical=False)
            centered.add(UILabel(text="", width=(self.window.width - 400) // 2))
            centered.add(UILabel(text=text, font_size=18, text_color=color, width=400, align="center"))
            centered.add(UILabel(text="", width=(self.window.width - 400) // 2))
            main_box.add(centered)

        main_box.add(UILabel(text="", height=30))

        records_label = UILabel(
            text="🏅 ГЛОБАЛЬНЫЕ РЕКОРДЫ:",
            font_size=22, text_color=arcade.color.GOLD,
            width=self.window.width - 100, align="center"
        )
        main_box.add(records_label)

        top_records = self.db.get_top_global_records(5)
        if top_records:
            for i, (rec_username, score, levels, date_str) in enumerate(top_records, 1):
                medal = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣"][i-1] if i <= 5 else f"{i}."
                row = UIBoxLayout(vertical=False, space_between=10)
                row.add(UILabel(text="", width=(self.window.width - 600) // 2))
                row.add(UILabel(text=f"{medal} {rec_username}", font_size=16,
                                text_color=arcade.color.GOLD if i <= 3 else arcade.color.WHITE,
                                width=200, align="left"))
                row.add(UILabel(text=str(score), font_size=16, width=100, align="center"))
                row.add(UILabel(text=f"{levels}/3", font_size=16, width=100, align="center"))
                try:
                    date_obj = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
                    date_fmt = date_obj.strftime("%d.%m.%Y")
                except:
                    date_fmt = date_str
                row.add(UILabel(text=date_fmt, font_size=14, text_color=arcade.color.LIGHT_GRAY,
                                width=120, align="center"))
                row.add(UILabel(text="", width=(self.window.width - 600) // 2))
                main_box.add(row)

        main_box.add(UILabel(text="", height=50))

        # Кнопки
        buttons_container = UIBoxLayout(vertical=False, space_between=20)
        left_spacer = UIBoxLayout(vertical=True)
        left_spacer.add(UILabel(text="", width=(self.window.width - 640) // 2, height=50))
        buttons_container.add(left_spacer)

        new_game_button = UIFlatButton(text="🔄 Новая игра", width=200, height=50)
        @new_game_button.event("on_click")
        def on_new_game(event):
            self.callback('new_game')
        buttons_container.add(new_game_button)

        menu_button = UIFlatButton(text="🏠 В главное меню", width=200, height=50)
        @menu_button.event("on_click")
        def on_menu(event):
            self.callback('to_menu')
        buttons_container.add(menu_button)

        exit_button = UIFlatButton(text="🚪 Выход", width=200, height=50)
        @exit_button.event("on_click")
        def on_exit(event):
            arcade.exit()
        buttons_container.add(exit_button)

        right_spacer = UIBoxLayout(vertical=True)
        right_spacer.add(UILabel(text="", width=(self.window.width - 640) // 2, height=50))
        buttons_container.add(right_spacer)

        main_box.add(buttons_container)
        self.ui_manager.add(main_box)

        if self.user_id:
            self.db.save_global_record(self.user_id, self.total_stats)
            self.db.update_player_progress(self.user_id, 3, 3)

    def on_draw(self):
        self.clear()
        # Конфетти
        for _ in range(100):
            x = random.randint(0, self.window.width)
            y = random.randint(0, self.window.height)
            color = random.choice([arcade.color.GOLD, arcade.color.SILVER, arcade.color.RED,
                                   arcade.color.GREEN, arcade.color.BLUE])
            shape = random.choice(['circle', 'square'])
            if shape == 'circle':
                arcade.draw_circle_filled(x, y, 4, color)
            else:
                arcade.draw_rectangle_filled(x, y, 8, 8, color)
        self.ui_manager.draw()
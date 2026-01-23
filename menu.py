# menu.py
import arcade
import sqlite3
import random
from arcade.gui import UIManager, UIBoxLayout, UIAnchorWidget, UIFlatButton, UILabel, UIInputText
from arcade.gui.widgets.layout import UIBoxGroup
from typing import Dict, List, Tuple, Optional, Any, Callable
from datetime import datetime
from database import GameDatabase


class StartMenuWindow(arcade.Window):
    """Стартовое меню игры с выбором уровня и авторизацией"""

    def __init__(self, width: int, height: int, title: str):
        super().__init__(width, height, title)

        self.ui_manager = UIManager()
        self.db = GameDatabase()
        self.current_user = None
        self.current_user_id = None

        self.setup_ui()

    def setup_ui(self):
        """Настройка интерфейса стартового меню"""
        self.ui_manager.purge_ui_elements()

        # Фон с анимированными звездами
        self.background_color = arcade.color.DARK_SLATE_BLUE
        self.stars = []
        for _ in range(100):
            self.stars.append({
                'x': random.randint(0, self.width),
                'y': random.randint(0, self.height),
                'size': random.uniform(0.5, 3.0),
                'speed': random.uniform(0.1, 0.5),
                'brightness': random.uniform(0.3, 1.0)
            })

        # Основной контейнер
        main_box = UIBoxLayout(vertical=True, align="center", space_between=30)

        # Заголовок игры
        title_label = UILabel(
            text="🚀 ЗАВОДЫ И ТАУЭР ДЕФЕНС 🚀",
            font_size=36,
            font_name="Kenney Future",
            text_color=arcade.color.GOLD,
            width=600,
            align="center"
        )
        main_box.add(title_label)

        # Подзаголовок
        subtitle_label = UILabel(
            text="Защити ядро, строй заводы, управляй дронами!",
            font_size=18,
            text_color=arcade.color.LIGHT_GRAY,
            width=500,
            align="center"
        )
        main_box.add(subtitle_label)

        # Блок авторизации/регистрации
        auth_container = UIBoxLayout(vertical=True, align="center", space_between=15)

        auth_label = UILabel(
            text="Введите имя игрока:",
            font_size=20,
            text_color=arcade.color.LIGHT_BLUE
        )
        auth_container.add(auth_label)

        self.username_input = UIInputText(
            width=300,
            height=40,
            font_size=18,
            text_color=arcade.color.BLACK,
            placeholder_text="Ваше имя"
        )
        auth_container.add(self.username_input)

        login_button = UIFlatButton(
            text="Войти / Зарегистрироваться",
            width=300,
            height=40
        )

        @login_button.event("on_click")
        def on_login(event):
            username = self.username_input.text.strip()
            if username:
                self.login_user(username)

        auth_container.add(login_button)
        main_box.add(auth_container)

        # Блок выбора уровня (будет показан после авторизации)
        self.level_container = UIBoxLayout(vertical=True, align="center", space_between=10)
        self.level_container.visible = False
        main_box.add(self.level_container)

        # Кнопка выхода
        exit_button = UIFlatButton(
            text="Выход",
            width=200,
            height=40
        )

        @exit_button.event("on_click")
        def on_exit(event):
            arcade.exit()

        main_box.add(exit_button)

        # Добавляем всё в менеджер
        self.ui_manager.add(UIAnchorWidget(
            anchor_x="center",
            anchor_y="center",
            child=main_box
        ))

    def login_user(self, username: str):
        """Авторизация/регистрация пользователя"""
        self.current_user_id = self.db.register_user(username)
        if self.current_user_id > 0:
            self.current_user = username
            self.show_level_selection()

    def show_level_selection(self):
        """Показ выбора уровней после авторизации"""
        self.level_container.clear()
        self.level_container.visible = True

        # Получаем прогресс пользователя
        user_stats = self.db.get_user_stats(self.current_user_id)
        unlocked_levels = user_stats.get('unlocked_levels', 1)

        title_label = UILabel(
            text=f"Добро пожаловать, {self.current_user}!",
            font_size=24,
            text_color=arcade.color.LIGHT_GREEN
        )
        self.level_container.add(title_label)

        # Кнопки уровней
        total_levels = 5  # Всего уровней в игре
        for level in range(1, total_levels + 1):
            level_box = UIBoxLayout(vertical=False, align="center", space_between=10)

            # Иконка уровня
            icon = "🔓" if level <= unlocked_levels else "🔒"
            color = arcade.color.GREEN if level <= unlocked_levels else arcade.color.GRAY

            level_button = UIFlatButton(
                text=f"{icon} Уровень {level}",
                width=200,
                height=50,
                style={
                    "font_name": "Arial",
                    "font_size": 18,
                    "bg_color": color if level <= unlocked_levels else arcade.color.DARK_GRAY,
                    "bg_color_pressed": arcade.color.DARK_GREEN if level <= unlocked_levels else arcade.color.DARK_GRAY
                }
            )

            # Получаем лучший результат для этого уровня
            level_records = self.db.get_user_level_records(self.current_user_id)
            record = level_records.get(level, {})

            if level <= unlocked_levels:
                @level_button.event("on_click")
                def on_level_click(event, lvl=level):
                    self.start_level(lvl)

            level_box.add(level_button)

            # Отображение лучшего счета
            if record:
                record_label = UILabel(
                    text=f"🏆 {record.get('score', 0)}",
                    font_size=14,
                    text_color=arcade.color.GOLD
                )
                level_box.add(record_label)

            self.level_container.add(level_box)

        # Кнопка продолжить (есть сохранение)
        saved_state = self.db.load_game_state(self.current_user_id)
        if saved_state:
            continue_button = UIFlatButton(
                text="🎮 Продолжить игру",
                width=250,
                height=50
            )

            @continue_button.event("on_click")
            def on_continue(event):
                self.continue_game()

            self.level_container.add(continue_button)

    def start_level(self, level_number: int):
        """Запуск выбранного уровня"""
        from game import MyGame
        self.close()

        # Здесь нужно передать level_number в игру
        game = MyGame(800, 600, f"Уровень {level_number}", f"level{level_number}.json")
        game.current_user_id = self.current_user_id
        game.current_user = self.current_user
        game.current_level = level_number

        # Загружаем сохраненное состояние, если есть
        saved_state = self.db.load_game_state(self.current_user_id)
        if saved_state:
            # Здесь можно восстановить состояние игры
            pass

        arcade.run()

    def continue_game(self):
        """Продолжение сохраненной игры"""
        saved_state = self.db.load_game_state(self.current_user_id)
        if saved_state:
            level = saved_state.get('current_level', 1)
            self.start_level(level)

    def on_draw(self):
        """Отрисовка меню"""
        self.clear(self.background_color)

        # Рисуем звездный фон
        for star in self.stars:
            brightness = int(255 * star['brightness'])
            arcade.draw_circle_filled(
                star['x'], star['y'], star['size'],
                (brightness, brightness, brightness)
            )

        # Рисуем UI
        self.ui_manager.draw()

        # Рисуем статистику в углу, если пользователь авторизован
        if self.current_user:
            stats = self.db.get_user_stats(self.current_user_id)
            arcade.draw_text(
                f"Игрок: {self.current_user}",
                10, self.height - 30,
                arcade.color.LIGHT_GRAY, 14
            )
            arcade.draw_text(
                f"Уровней пройдено: {stats.get('unlocked_levels', 1)}",
                10, self.height - 50,
                arcade.color.LIGHT_GRAY, 12
            )

    def on_update(self, delta_time: float):
        """Обновление анимации"""
        # Анимируем звезды
        for star in self.stars:
            star['y'] += star['speed']
            if star['y'] > self.height:
                star['y'] = 0
                star['x'] = random.randint(0, self.width)

    def on_close(self):
        """Закрытие окна"""
        self.db.close()
        super().on_close()


class LevelCompleteWindow(arcade.Window):
    """Окно после успешного прохождения уровня"""

    def __init__(self, width: int = 800, height: int = 600,
                 level_data: Dict[str, Any] = None,
                 user_id: int = None,
                 username: str = None,
                 callback: Callable = None):
        super().__init__(width, height, "Уровень пройден!")

        self.level_data = level_data or {}
        self.user_id = user_id
        self.username = username
        self.callback = callback  # Функция обратного вызова для перехода
        self.db = GameDatabase()

        self.ui_manager = UIManager()
        self.setup_ui()

    def setup_ui(self):
        """Настройка интерфейса"""
        self.ui_manager.purge_ui_elements()

        # Фон
        self.background_color = arcade.color.DARK_GREEN

        # Основной контейнер
        main_box = UIBoxLayout(vertical=True, align="center", space_between=20)

        # Заголовок
        title_label = UILabel(
            text="🎉 УРОВЕНЬ ПРОЙДЕН! 🎉",
            font_size=36,
            font_name="Kenney Future",
            text_color=arcade.color.GOLD,
            width=600,
            align="center"
        )
        main_box.add(title_label)

        # Информация об уровне
        level_info = UILabel(
            text=f"Уровень {self.level_data.get('level_number', 1)}",
            font_size=24,
            text_color=arcade.color.LIGHT_GREEN
        )
        main_box.add(level_info)

        # Статистика уровня
        stats_box = UIBoxLayout(vertical=True, align="left", space_between=8)

        stats = [
            (f"🏆 Очки: {self.level_data.get('score', 0)}", arcade.color.GOLD),
            (f"🎯 Убито врагов: {self.level_data.get('enemies_killed', 0)}", arcade.color.RED),
            (f"⏱️ Время: {self.level_data.get('time_spent', 0):.1f} сек", arcade.color.CYAN),
            (f"🌊 Волн пройдено: {self.level_data.get('waves_completed', 0)}", arcade.color.BLUE),
            (f"🏭 Построено зданий: {self.level_data.get('buildings_built', 0)}", arcade.color.BROWN),
            (f"🚁 Использовано дронов: {self.level_data.get('drones_used', 0)}", arcade.color.SILVER)
        ]

        for text, color in stats:
            stats_box.add(UILabel(
                text=text,
                font_size=18,
                text_color=color
            ))

        main_box.add(stats_box)

        # Награды
        rewards = self.calculate_rewards()
        if rewards:
            rewards_box = UIBoxLayout(vertical=True, align="center", space_between=5)
            rewards_box.add(UILabel(
                text="🎁 Полученные награды:",
                font_size=20,
                text_color=arcade.color.LIGHT_YELLOW
            ))

            for reward in rewards:
                rewards_box.add(UILabel(
                    text=f"• {reward}",
                    font_size=16,
                    text_color=arcade.color.LIGHT_GREEN
                ))

            main_box.add(rewards_box)

        # Кнопки действий
        buttons_box = UIBoxLayout(vertical=False, align="center", space_between=20)

        # Кнопка "Следующий уровень"
        next_button = UIFlatButton(
            text="▶ Следующий уровень",
            width=200,
            height=50
        )

        @next_button.event("on_click")
        def on_next(event):
            self.close()
            if self.callback:
                self.callback('next_level')

        buttons_box.add(next_button)

        # Кнопка "Повторить"
        retry_button = UIFlatButton(
            text="🔄 Повторить",
            width=200,
            height=50
        )

        @retry_button.event("on_click")
        def on_retry(event):
            self.close()
            if self.callback:
                self.callback('retry_level')

        buttons_box.add(retry_button)

        # Кнопка "В меню"
        menu_button = UIFlatButton(
            text="🏠 В меню",
            width=200,
            height=50
        )

        @menu_button.event("on_click")
        def on_menu(event):
            self.close()
            if self.callback:
                self.callback('to_menu')

        buttons_box.add(menu_button)

        main_box.add(buttons_box)

        # Добавляем всё в менеджер
        self.ui_manager.add(UIAnchorWidget(
            anchor_x="center",
            anchor_y="center",
            child=main_box
        ))

        # Сохраняем результат
        if self.user_id:
            self.db.save_level_record(self.user_id, self.level_data)

    def calculate_rewards(self) -> List[str]:
        """Вычисление наград за уровень"""
        rewards = []
        score = self.level_data.get('score', 0)

        if score > 2000:
            rewards.append("Золотая медаль 🥇")
        elif score > 1500:
            rewards.append("Серебряная медаль 🥈")
        elif score > 1000:
            rewards.append("Бронзовая медаль 🥉")

        if self.level_data.get('enemies_killed', 0) > 50:
            rewards.append("Мастер истребитель 🎯")

        if self.level_data.get('time_spent', 0) < 120:
            rewards.append("Скоростной проход ⚡")

        return rewards

    def on_draw(self):
        """Отрисовка окна"""
        self.clear(self.background_color)

        # Рисуем праздничные эффекты
        self.draw_celebration()
        self.ui_manager.draw()

    def draw_celebration(self):
        """Рисуем праздничные эффекты"""
        import random
        for i in range(50):
            x = random.randint(0, self.width)
            y = random.randint(0, self.height)
            color = random.choice([
                arcade.color.GOLD, arcade.color.SILVER, arcade.color.BRONZE,
                arcade.color.RED, arcade.color.GREEN, arcade.color.BLUE
            ])
            arcade.draw_circle_filled(x, y, 2, color)

    def on_close(self):
        """Закрытие окна"""
        self.db.close()
        super().on_close()


class GameOverWindow(arcade.Window):
    """Окно после поражения"""

    def __init__(self, width: int = 800, height: int = 600,
                 level_number: int = 1,
                 reason: str = "Ядро разрушено",
                 stats: Dict[str, Any] = None,
                 user_id: int = None,
                 callback: Callable = None):
        super().__init__(width, height, "Поражение")

        self.level_number = level_number
        self.reason = reason
        self.stats = stats or {}
        self.user_id = user_id
        self.callback = callback
        self.db = GameDatabase()

        self.ui_manager = UIManager()
        self.setup_ui()

    def setup_ui(self):
        """Настройка интерфейса"""
        self.ui_manager.purge_ui_elements()

        # Фон
        self.background_color = arcade.color.DARK_RED

        # Основной контейнер
        main_box = UIBoxLayout(vertical=True, align="center", space_between=20)

        # Заголовок
        title_label = UILabel(
            text="💀 ПОРАЖЕНИЕ 💀",
            font_size=36,
            font_name="Kenney Future",
            text_color=arcade.color.BLACK,
            width=600,
            align="center"
        )
        main_box.add(title_label)

        # Причина поражения
        reason_label = UILabel(
            text=f"Причина: {self.reason}",
            font_size=24,
            text_color=arcade.color.WHITE
        )
        main_box.add(reason_label)

        # Уровень
        level_label = UILabel(
            text=f"Уровень {self.level_number}",
            font_size=20,
            text_color=arcade.color.LIGHT_GRAY
        )
        main_box.add(level_label)

        # Достигнутый прогресс
        if self.stats:
            progress_box = UIBoxLayout(vertical=True, align="left", space_between=8)

            progress_label = UILabel(
                text="Достигнутый прогресс:",
                font_size=20,
                text_color=arcade.color.LIGHT_YELLOW
            )
            progress_box.add(progress_label)

            stats_items = [
                (f"🏆 Очки: {self.stats.get('score', 0)}", arcade.color.GOLD),
                (f"🎯 Убито врагов: {self.stats.get('enemies_killed', 0)}", arcade.color.RED),
                (f"⏱️ Время выживания: {self.stats.get('time_survived', 0):.1f} сек", arcade.color.CYAN),
                (f"🌊 Волн пройдено: {self.stats.get('waves_completed', 0)}", arcade.color.BLUE)
            ]

            for text, color in stats_items:
                progress_box.add(UILabel(
                    text=text,
                    font_size=16,
                    text_color=color
                ))

            main_box.add(progress_box)

        # Советы по улучшению
        tips = self.get_tips()
        if tips:
            tips_box = UIBoxLayout(vertical=True, align="center", space_between=5)
            tips_box.add(UILabel(
                text="💡 Советы для следующей попытки:",
                font_size=18,
                text_color=arcade.color.LIGHT_BLUE
            ))

            for tip in tips:
                tips_box.add(UILabel(
                    text=f"• {tip}",
                    font_size=14,
                    text_color=arcade.color.LIGHT_GRAY
                ))

            main_box.add(tips_box)

        # Кнопки действий
        buttons_box = UIBoxLayout(vertical=False, align="center", space_between=20)

        # Кнопка "Повторить"
        retry_button = UIFlatButton(
            text="🔄 Повторить уровень",
            width=200,
            height=50,
            style={
                "bg_color": arcade.color.DARK_GREEN,
                "bg_color_pressed": arcade.color.GREEN
            }
        )

        @retry_button.event("on_click")
        def on_retry(event):
            self.close()
            if self.callback:
                self.callback('retry_level')

        buttons_box.add(retry_button)

        # Кнопка "В меню"
        menu_button = UIFlatButton(
            text="🏠 В главное меню",
            width=200,
            height=50
        )

        @menu_button.event("on_click")
        def on_menu(event):
            self.close()
            if self.callback:
                self.callback('to_menu')

        buttons_box.add(menu_button)

        main_box.add(buttons_box)

        # Добавляем всё в менеджер
        self.ui_manager.add(UIAnchorWidget(
            anchor_x="center",
            anchor_y="center",
            child=main_box
        ))

    def get_tips(self) -> List[str]:
        """Генерация советов по улучшению игры"""
        tips = []

        if self.reason == "Ядро разрушено":
            tips.append("Стройте больше турелей вокруг ядра")
            tips.append("Улучшайте существующие турели")
            tips.append("Стройте стены для защиты ядра")

        if self.stats.get('enemies_killed', 0) < 10:
            tips.append("Фокусируйтесь на убийстве врагов")
            tips.append("Используйте комбинации турелей")

        if self.stats.get('waves_completed', 0) < 3:
            tips.append("Улучшайте экономику в начале волн")
            tips.append("Стройте больше буров для ресурсов")

        return tips[:3]  # Возвращаем не более 3 советов

    def on_draw(self):
        """Отрисовка окна"""
        self.clear(self.background_color)

        # Рисуем трещины на экране
        self.draw_cracks()
        self.ui_manager.draw()

    def draw_cracks(self):
        """Рисуем трещины для эффекта разбитого экрана"""
        arcade.draw_line(100, 100, 700, 500, arcade.color.BLACK, 3)
        arcade.draw_line(200, 500, 600, 200, arcade.color.BLACK, 3)
        arcade.draw_line(400, 100, 400, 500, arcade.color.BLACK, 2)

    def on_close(self):
        """Закрытие окна"""
        self.db.close()
        super().on_close()


class FinalResultsWindow(arcade.Window):
    """Финальное окно после прохождения всех уровней"""

    def __init__(self, width: int = 800, height: int = 600,
                 total_stats: Dict[str, Any] = None,
                 user_id: int = None,
                 username: str = None,
                 callback: Callable = None):
        super().__init__(width, height, "Игра пройдена!")

        self.total_stats = total_stats or {}
        self.user_id = user_id
        self.username = username
        self.callback = callback
        self.db = GameDatabase()

        self.ui_manager = UIManager()
        self.setup_ui()

    def setup_ui(self):
        """Настройка интерфейса"""
        self.ui_manager.purge_ui_elements()

        # Фон
        self.background_color = arcade.color.DARK_BLUE

        # Основной контейнер с прокруткой
        main_box = UIBoxLayout(vertical=True, align="center", space_between=20)

        # Заголовок
        title_label = UILabel(
            text="🏆 ИГРА ПРОЙДЕНА! 🏆",
            font_size=36,
            font_name="Kenney Future",
            text_color=arcade.color.GOLD,
            width=600,
            align="center"
        )
        main_box.add(title_label)

        # Поздравление
        congrats_label = UILabel(
            text=f"Поздравляем, {self.username}!",
            font_size=24,
            text_color=arcade.color.LIGHT_GREEN
        )
        main_box.add(congrats_label)

        # Общая статистика
        total_box = UIBoxLayout(vertical=True, align="center", space_between=10)

        total_label = UILabel(
            text="📊 ОБЩАЯ СТАТИСТИКА:",
            font_size=22,
            text_color=arcade.color.LIGHT_BLUE
        )
        total_box.add(total_label)

        total_stats_items = [
            (f"🏆 Общий счет: {self.total_stats.get('total_score', 0)}", arcade.color.GOLD),
            (f"🎯 Всего врагов убито: {self.total_stats.get('total_enemies_killed', 0)}", arcade.color.RED),
            (f"⏱️ Общее время игры: {self.total_stats.get('total_play_time', 0):.1f} сек", arcade.color.CYAN),
            (f"🌊 Всего уровней пройдено: {self.total_stats.get('levels_completed', 0)}", arcade.color.BLUE)
        ]

        for text, color in total_stats_items:
            total_box.add(UILabel(
                text=text,
                font_size=18,
                text_color=color
            ))

        main_box.add(total_box)

        # Детальная статистика по уровням
        if self.user_id:
            level_records = self.db.get_user_level_records(self.user_id)
            if level_records:
                levels_box = UIBoxLayout(vertical=True, align="center", space_between=10)

                levels_label = UILabel(
                    text="📈 РЕЗУЛЬТАТЫ ПО УРОВНЯМ:",
                    font_size=22,
                    text_color=arcade.color.LIGHT_BLUE
                )
                levels_box.add(levels_label)

                # Таблица уровней
                for level_num, record in sorted(level_records.items()):
                    level_row = UIBoxLayout(vertical=False, align="center", space_between=30)

                    # Номер уровня
                    level_row.add(UILabel(
                        text=f"Уровень {level_num}",
                        font_size=16,
                        text_color=arcade.color.WHITE,
                        width=100
                    ))

                    # Очки
                    level_row.add(UILabel(
                        text=f"{record['score']} очков",
                        font_size=16,
                        text_color=arcade.color.GOLD,
                        width=120
                    ))

                    # Время
                    level_row.add(UILabel(
                        text=f"{record['time_spent']:.1f} сек",
                        font_size=16,
                        text_color=arcade.color.CYAN,
                        width=100
                    ))

                    # Волны
                    level_row.add(UILabel(
                        text=f"{record['waves_completed']} волн",
                        font_size=16,
                        text_color=arcade.color.BLUE,
                        width=100
                    ))

                    levels_box.add(level_row)

                main_box.add(levels_box)

        # Таблица глобальных рекордов
        records_box = UIBoxLayout(vertical=True, align="center", space_between=10)

        records_label = UILabel(
            text="🏅 ГЛОБАЛЬНЫЕ РЕКОРДЫ:",
            font_size=22,
            text_color=arcade.color.GOLD
        )
        records_box.add(records_label)

        top_records = self.db.get_top_global_records(5)
        if top_records:
            for i, (username, score, levels, date_str) in enumerate(top_records, 1):
                medal = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣"][i - 1] if i <= 5 else f"{i}."

                record_row = UIBoxLayout(vertical=False, align="center", space_between=20)

                record_row.add(UILabel(
                    text=f"{medal} {username}",
                    font_size=16,
                    text_color=arcade.color.GOLD if i <= 3 else arcade.color.WHITE,
                    width=200
                ))

                record_row.add(UILabel(
                    text=f"{score} очков",
                    font_size=16,
                    width=150
                ))

                record_row.add(UILabel(
                    text=f"{levels} уровней",
                    font_size=16,
                    width=100
                ))

                # Форматируем дату
                try:
                    date_obj = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
                    date_formatted = date_obj.strftime("%d.%m.%Y")
                except:
                    date_formatted = date_str

                record_row.add(UILabel(
                    text=date_formatted,
                    font_size=14,
                    text_color=arcade.color.LIGHT_GRAY,
                    width=120
                ))

                records_box.add(record_row)

        main_box.add(records_box)

        # Кнопки действий
        buttons_box = UIBoxLayout(vertical=False, align="center", space_between=20)

        # Кнопка "Новая игра"
        new_game_button = UIFlatButton(
            text="🔄 Новая игра",
            width=200,
            height=50
        )

        @new_game_button.event("on_click")
        def on_new_game(event):
            self.close()
            if self.callback:
                self.callback('new_game')

        buttons_box.add(new_game_button)

        # Кнопка "В меню"
        menu_button = UIFlatButton(
            text="🏠 В главное меню",
            width=200,
            height=50
        )

        @menu_button.event("on_click")
        def on_menu(event):
            self.close()
            if self.callback:
                self.callback('to_menu')

        buttons_box.add(menu_button)

        # Кнопка "Выход"
        exit_button = UIFlatButton(
            text="🚪 Выход",
            width=200,
            height=50
        )

        @exit_button.event("on_click")
        def on_exit(event):
            arcade.exit()

        buttons_box.add(exit_button)

        main_box.add(buttons_box)

        # Добавляем всё в менеджер
        self.ui_manager.add(UIAnchorWidget(
            anchor_x="center",
            anchor_y="top",
            child=main_box
        ))

        # Сохраняем глобальный рекорд
        if self.user_id:
            self.db.save_global_record(self.user_id, self.total_stats)
            # Разблокируем все уровни
            self.db.update_player_progress(self.user_id,
                                           self.total_stats.get('levels_completed', 1),
                                           self.total_stats.get('levels_completed', 1))

    def on_draw(self):
        """Отрисовка окна"""
        self.clear(self.background_color)

        # Рисуем праздничный фон
        self.draw_celebration_background()
        self.ui_manager.draw()

    def draw_celebration_background(self):
        """Рисуем праздничный фон с конфетти"""
        import random
        # Конфетти
        for i in range(100):
            x = random.randint(0, self.width)
            y = random.randint(0, self.height)
            color = random.choice([
                arcade.color.GOLD, arcade.color.SILVER, arcade.color.BRONZE,
                arcade.color.RED, arcade.color.GREEN, arcade.color.BLUE,
                arcade.color.PURPLE, arcade.color.YELLOW
            ])
            shape = random.choice(['circle', 'square', 'triangle'])

            if shape == 'circle':
                arcade.draw_circle_filled(x, y, 4, color)
            elif shape == 'square':
                arcade.draw_rectangle_filled(x, y, 8, 8, color)
            else:  # triangle
                points = [(x, y + 5), (x - 5, y - 5), (x + 5, y - 5)]
                arcade.draw_polygon_filled(points, color)

    def on_close(self):
        """Закрытие окна"""
        self.db.close()
        super().on_close()


# Вспомогательная функция для перехода между окнами
def show_level_complete(level_data: Dict[str, Any], user_id: int, username: str):
    """Показать окно завершения уровня"""
    window = LevelCompleteWindow(
        level_data=level_data,
        user_id=user_id,
        username=username,
        callback=handle_level_complete_callback
    )
    return window


def show_game_over(level_number: int, reason: str, stats: Dict[str, Any], user_id: int):
    """Показать окно поражения"""
    window = GameOverWindow(
        level_number=level_number,
        reason=reason,
        stats=stats,
        user_id=user_id,
        callback=handle_game_over_callback
    )
    return window


def show_final_results(total_stats: Dict[str, Any], user_id: int, username: str):
    """Показать финальное окно результатов"""
    window = FinalResultsWindow(
        total_stats=total_stats,
        user_id=user_id,
        username=username,
        callback=handle_final_results_callback
    )
    return window


# Обработчики обратных вызовов (должны быть реализованы в game.py)
def handle_level_complete_callback(action: str):
    """Обработка выбора игрока после завершения уровня"""
    print(f"Выбрано действие: {action}")
    # Здесь должна быть логика перехода к следующему уровню/повтору/меню


def handle_game_over_callback(action: str):
    """Обработка выбора игрока после поражения"""
    print(f"Выбрано действие после поражения: {action}")


def handle_final_results_callback(action: str):
    """Обработка выбора игрока после финальных результатов"""
    print(f"Выбрано действие после завершения игры: {action}")
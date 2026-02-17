import arcade
import sqlite3
import random
from arcade.gui import UIManager, UIBoxLayout, UIFlatButton, UILabel, UIInputText
from typing import Dict, List, Tuple, Optional, Any, Callable
from datetime import datetime
from database import GameDatabase

class StartMenuWindow(arcade.Window):
    """Стартовое меню игры с выбором уровня и авторизацией"""

    def __init__(self, width: int, height: int, title: str):
        super().__init__(width, height, title)

        self.ui_manager = UIManager()
        self.ui_manager.enable()
        self.db = GameDatabase()
        self.current_user = None
        self.current_user_id = None

        self.background_color = arcade.color.DARK_SLATE_BLUE
        self.setup_ui()

    def setup_ui(self):
        """Настройка интерфейса стартового меню"""
        self.ui_manager.clear()

        # Создаем основную вертикальную коробку
        v_box = UIBoxLayout(vertical=True, space_between=20)

        # Пустое пространство сверху для центрирования
        top_spacer = UIBoxLayout(vertical=False)
        top_spacer.add(UILabel(text="", width=self.width, height=100))
        v_box.add(top_spacer)

        # Заголовок игры
        title_label = UILabel(
            text="🚀 ЗАВОДЫ И ТАУЭР ДЕФЕНС 🚀",
            font_size=36,
            font_name="Kenney Future",
            text_color=arcade.color.GOLD,
            width=self.width - 100,
            align="center"
        )
        v_box.add(title_label)

        # Подзаголовок
        subtitle_label = UILabel(
            text="Защити ядро, строй заводы, управляй дронами!",
            font_size=18,
            text_color=arcade.color.LIGHT_GRAY,
            width=self.width - 100,
            align="center"
        )
        v_box.add(subtitle_label)

        # Пустое пространство
        v_box.add(UILabel(text="", height=30))

        # Блок авторизации/регистрации
        auth_container = UIBoxLayout(vertical=True, space_between=10)

        auth_label = UILabel(
            text="Введите имя игрока:",
            font_size=20,
            text_color=arcade.color.LIGHT_BLUE,
            width=300,
            align="center"
        )
        auth_container.add(auth_label)

        self.username_input = UIInputText(
            width=300,
            height=40,
            font_size=18,
            text_color=arcade.color.BLACK
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

        # Центрируем контейнер авторизации
        auth_centered = UIBoxLayout(vertical=False)
        auth_centered.add(UILabel(text="", width=(self.width - 300) // 2))
        auth_centered.add(auth_container)
        auth_centered.add(UILabel(text="", width=(self.width - 300) // 2))

        v_box.add(auth_centered)

        # Блок выбора уровня (будет показан после авторизации)
        self.level_container = UIBoxLayout(vertical=True, space_between=10)
        v_box.add(self.level_container)

        # Кнопка выхода
        exit_centered = UIBoxLayout(vertical=False)
        exit_centered.add(UILabel(text="", width=(self.width - 200) // 2))

        exit_button = UIFlatButton(
            text="Выход",
            width=200,
            height=40
        )

        @exit_button.event("on_click")
        def on_exit(event):
            arcade.exit()

        exit_centered.add(exit_button)
        exit_centered.add(UILabel(text="", width=(self.width - 200) // 2))

        v_box.add(exit_centered)

        # Добавляем всё в менеджер
        self.ui_manager.add(v_box)

    def login_user(self, username: str):
        """Авторизация/регистрация пользователя"""
        self.current_user_id = self.db.register_user(username)
        if self.current_user_id > 0:
            self.current_user = username
            self.show_level_selection()

    def show_level_selection(self):
        """Показ выбора уровней после авторизации"""
        self.level_container.clear()

        # Получаем прогресс пользователя
        user_stats = self.db.get_user_stats(self.current_user_id)
        unlocked_levels = user_stats.get('unlocked_levels', 1)

        title_label = UILabel(
            text=f"Добро пожаловать, {self.current_user}!",
            font_size=24,
            text_color=arcade.color.LIGHT_GREEN,
            width=self.width - 100,
            align="center"
        )
        self.level_container.add(title_label)

        # Кнопки уровней
        total_levels = 3  # Всего 3 уровня в игре
        for level in range(1, total_levels + 1):
            # Создаем контейнер для центрирования кнопки
            level_centered = UIBoxLayout(vertical=False)
            level_centered.add(UILabel(text="", width=(self.width - 250) // 2))

            # Иконка уровня
            icon = "🔓" if level <= unlocked_levels else "🔒"
            level_button = UIFlatButton(
                text=f"{icon} Уровень {level}",
                width=200,
                height=50
            )

            if level <= unlocked_levels:
                @level_button.event("on_click")
                def on_level_click(event, lvl=level):
                    self.start_level(lvl)

            level_centered.add(level_button)

            # Получаем лучший результат для этого уровня
            level_records = self.db.get_user_level_records(self.current_user_id)
            record = level_records.get(level, {})

            if record:
                record_label = UILabel(
                    text=f"🏆 {record.get('score', 0)}",
                    font_size=14,
                    text_color=arcade.color.GOLD,
                    width=50,
                    align="center"
                )
                level_centered.add(record_label)
            else:
                level_centered.add(UILabel(text="", width=50))

            level_centered.add(UILabel(text="", width=(self.width - 250) // 2))
            self.level_container.add(level_centered)

        # Кнопка продолжить (есть сохранение)
        saved_state = self.db.load_game_state(self.current_user_id)
        if saved_state:
            continue_centered = UIBoxLayout(vertical=False)
            continue_centered.add(UILabel(text="", width=(self.width - 250) // 2))

            continue_button = UIFlatButton(
                text="🎮 Продолжить игру",
                width=250,
                height=50
            )

            @continue_button.event("on_click")
            def on_continue(event):
                self.continue_game()

            continue_centered.add(continue_button)
            continue_centered.add(UILabel(text="", width=(self.width - 250) // 2))
            self.level_container.add(continue_centered)

    def start_level(self, level_number: int):
        """Запуск выбранного уровня"""
        from game import MyGame

        game = MyGame(800, 600, f"Уровень {level_number}")  # убран второй аргумент с картой
        game.current_user_id = self.current_user_id
        game.current_user = self.current_user
        game.current_level = level_number

        # Загружаем сохранённое состояние, если есть
        saved_state = self.db.load_game_state(self.current_user_id)
        if saved_state:
            # Здесь можно восстановить состояние игры
            pass

        arcade.run()
        self.close()

    def continue_game(self):
        """Продолжение сохраненной игры"""
        saved_state = self.db.load_game_state(self.current_user_id)
        if saved_state:
            level = saved_state.get('current_level', 1)
            self.start_level(level)

    def on_draw(self):
        """Отрисовка меню"""
        self.clear()

        # Рисуем звездный фон
        for star in getattr(self, 'stars', []):
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
        # Инициализируем звезды, если их еще нет
        if not hasattr(self, 'stars'):
            self.stars = []
            for _ in range(100):
                self.stars.append({
                    'x': random.randint(0, self.width),
                    'y': random.randint(0, self.height),
                    'size': random.uniform(0.5, 3.0),
                    'speed': random.uniform(0.1, 0.5),
                    'brightness': random.uniform(0.3, 1.0)
                })

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
        self.callback = callback
        self.db = GameDatabase()

        self.ui_manager = UIManager()
        self.ui_manager.enable()

        self.background_color = arcade.color.DARK_GREEN
        self.setup_ui()

    def setup_ui(self):
        """Настройка интерфейса"""
        self.ui_manager.clear()

        # Основная вертикальная коробка
        main_box = UIBoxLayout(vertical=True, space_between=15)

        # Пустое пространство сверху
        main_box.add(UILabel(text="", height=50))

        # Заголовок
        title_label = UILabel(
            text="🎉 УРОВЕНЬ ПРОЙДЕН! 🎉",
            font_size=36,
            font_name="Kenney Future",
            text_color=arcade.color.GOLD,
            width=self.width - 100,
            align="center"
        )
        main_box.add(title_label)

        # Информация об уровне
        level_info = UILabel(
            text=f"Уровень {self.level_data.get('level_number', 1)}",
            font_size=24,
            text_color=arcade.color.LIGHT_GREEN,
            width=self.width - 100,
            align="center"
        )
        main_box.add(level_info)

        # Пустое пространство
        main_box.add(UILabel(text="", height=20))

        # Статистика уровня
        for text, color in [
            (f"🏆 Очки: {self.level_data.get('score', 0)}", arcade.color.GOLD),
            (f"🎯 Убито врагов: {self.level_data.get('enemies_killed', 0)}", arcade.color.RED),
            (f"⏱️ Время: {self.level_data.get('time_spent', 0):.1f} сек", arcade.color.CYAN),
            (f"🌊 Волн пройдено: {self.level_data.get('waves_completed', 0)}", arcade.color.BLUE),
            (f"🏭 Построено зданий: {self.level_data.get('buildings_built', 0)}", arcade.color.BROWN),
            (f"🚁 Использовано дронов: {self.level_data.get('drones_used', 0)}", arcade.color.SILVER)
        ]:
            centered = UIBoxLayout(vertical=False)
            centered.add(UILabel(text="", width=(self.width - 400) // 2))
            centered.add(UILabel(
                text=text,
                font_size=18,
                text_color=color,
                width=400,
                align="center"
            ))
            centered.add(UILabel(text="", width=(self.width - 400) // 2))
            main_box.add(centered)

        # Награды
        rewards = self.calculate_rewards()
        if rewards:
            main_box.add(UILabel(text="", height=20))

            rewards_label = UILabel(
                text="🎁 Полученные награды:",
                font_size=20,
                text_color=arcade.color.LIGHT_YELLOW,
                width=self.width - 100,
                align="center"
            )
            main_box.add(rewards_label)

            for reward in rewards:
                centered = UIBoxLayout(vertical=False)
                centered.add(UILabel(text="", width=(self.width - 400) // 2))
                centered.add(UILabel(
                    text=f"• {reward}",
                    font_size=16,
                    text_color=arcade.color.LIGHT_GREEN,
                    width=400,
                    align="center"
                ))
                centered.add(UILabel(text="", width=(self.width - 400) // 2))
                main_box.add(centered)

        # Пустое пространство перед кнопками
        main_box.add(UILabel(text="", height=40))

        # Кнопки действий
        buttons_container = UIBoxLayout(vertical=False, space_between=20)

        # Центрируем кнопки
        left_spacer = UIBoxLayout(vertical=True)
        left_spacer.add(UILabel(text="", width=(self.width - 640) // 2, height=50))
        buttons_container.add(left_spacer)

        # Проверяем, последний ли это уровень
        current_level = self.level_data.get('level_number', 1)
        is_last_level = current_level >= 3  # 3 - последний уровень

        if not is_last_level:
            # Кнопка "Следующий уровень" (показываем только если не последний)
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

            buttons_container.add(next_button)

        # Кнопка "Повторить"
        retry_button = UIFlatButton(
            text="🔄 Повторить",
            width=200 if is_last_level else 200,  # Ширина зависит от того, показываем ли кнопку "Следующий"
            height=50
        )

        @retry_button.event("on_click")
        def on_retry(event):
            self.close()
            if self.callback:
                self.callback('retry_level')

        buttons_container.add(retry_button)

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

        buttons_container.add(menu_button)

        right_spacer = UIBoxLayout(vertical=True)
        right_spacer.add(UILabel(text="", width=(self.width - 640) // 2, height=50))
        buttons_container.add(right_spacer)

        main_box.add(buttons_container)

        # Добавляем всё в менеджер
        self.ui_manager.add(main_box)

        # Сохраняем результат
        if self.user_id:
            self.db.save_level_record(self.user_id, self.level_data)

    def calculate_rewards(self) -> List[str]:
        """Вычисление наград за уровень"""
        rewards = []
        score = self.level_data.get('score', 0)
        level = self.level_data.get('level_number', 1)

        # Базовые награды за уровень
        if level == 1:
            if score > 1000:
                rewards.append("Золотая медаль 🥇")
            elif score > 750:
                rewards.append("Серебряная медаль 🥈")
            elif score > 500:
                rewards.append("Бронзовая медаль 🥉")

        elif level == 2:
            if score > 2000:
                rewards.append("Золотая медаль 🥇")
            elif score > 1500:
                rewards.append("Серебряная медаль 🥈")
            elif score > 1000:
                rewards.append("Бронзовая медаль 🥉")

        elif level == 3:
            if score > 3000:
                rewards.append("Золотая медаль 🥇")
            elif score > 2000:
                rewards.append("Серебряная медаль 🥈")
            elif score > 1500:
                rewards.append("Бронзовая медаль 🥉")

        # Дополнительные награды
        if self.level_data.get('enemies_killed', 0) > 30:
            rewards.append("Мастер истребитель 🎯")

        if self.level_data.get('time_spent', 0) < 180:
            rewards.append("Скоростной проход ⚡")

        if level == 3:
            rewards.append("Завершение игры! 🏆")

        return rewards

    def on_draw(self):
        """Отрисовка окна"""
        self.clear()

        # Рисуем праздничные эффекты
        self.draw_celebration()
        self.ui_manager.draw()

    def draw_celebration(self):
        """Рисуем праздничные эффекты"""
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
        self.ui_manager.enable()

        self.background_color = arcade.color.DARK_RED
        self.setup_ui()

    def setup_ui(self):
        """Настройка интерфейса"""
        self.ui_manager.clear()

        # Основная вертикальная коробка
        main_box = UIBoxLayout(vertical=True, space_between=15)

        # Пустое пространство сверху
        main_box.add(UILabel(text="", height=80))

        # Заголовок
        title_label = UILabel(
            text="💀 ПОРАЖЕНИЕ 💀",
            font_size=36,
            font_name="Kenney Future",
            text_color=arcade.color.BLACK,
            width=self.width - 100,
            align="center"
        )
        main_box.add(title_label)

        # Причина поражения
        reason_label = UILabel(
            text=f"Причина: {self.reason}",
            font_size=24,
            text_color=arcade.color.WHITE,
            width=self.width - 100,
            align="center"
        )
        main_box.add(reason_label)

        # Уровень
        level_label = UILabel(
            text=f"Уровень {self.level_number}",
            font_size=20,
            text_color=arcade.color.LIGHT_GRAY,
            width=self.width - 100,
            align="center"
        )
        main_box.add(level_label)

        # Пустое пространство
        main_box.add(UILabel(text="", height=30))

        # Достигнутый прогресс
        if self.stats:
            progress_label = UILabel(
                text="Достигнутый прогресс:",
                font_size=20,
                text_color=arcade.color.LIGHT_YELLOW,
                width=self.width - 100,
                align="center"
            )
            main_box.add(progress_label)

            for text, color in [
                (f"🏆 Очки: {self.stats.get('score', 0)}", arcade.color.GOLD),
                (f"🎯 Убито врагов: {self.stats.get('enemies_killed', 0)}", arcade.color.RED),
                (f"⏱️ Время выживания: {self.stats.get('time_survived', 0):.1f} сек", arcade.color.CYAN),
                (f"🌊 Волн пройдено: {self.stats.get('waves_completed', 0)}", arcade.color.BLUE)
            ]:
                centered = UIBoxLayout(vertical=False)
                centered.add(UILabel(text="", width=(self.width - 400) // 2))
                centered.add(UILabel(
                    text=text,
                    font_size=16,
                    text_color=color,
                    width=400,
                    align="center"
                ))
                centered.add(UILabel(text="", width=(self.width - 400) // 2))
                main_box.add(centered)

        # Советы по улучшению
        tips = self.get_tips()
        if tips:
            main_box.add(UILabel(text="", height=20))

            tips_label = UILabel(
                text="💡 Советы для следующей попытки:",
                font_size=18,
                text_color=arcade.color.LIGHT_BLUE,
                width=self.width - 100,
                align="center"
            )
            main_box.add(tips_label)

            for tip in tips:
                centered = UIBoxLayout(vertical=False)
                centered.add(UILabel(text="", width=(self.width - 400) // 2))
                centered.add(UILabel(
                    text=f"• {tip}",
                    font_size=14,
                    text_color=arcade.color.LIGHT_GRAY,
                    width=400,
                    align="center"
                ))
                centered.add(UILabel(text="", width=(self.width - 400) // 2))
                main_box.add(centered)

        # Пустое пространство перед кнопками
        main_box.add(UILabel(text="", height=50))

        # Кнопки действий
        buttons_container = UIBoxLayout(vertical=False, space_between=20)

        # Центрируем кнопки
        left_spacer = UIBoxLayout(vertical=True)
        left_spacer.add(UILabel(text="", width=(self.width - 440) // 2, height=50))
        buttons_container.add(left_spacer)

        # Кнопка "Повторить"
        retry_button = UIFlatButton(
            text="🔄 Повторить уровень",
            width=200,
            height=50
        )

        @retry_button.event("on_click")
        def on_retry(event):
            self.close()
            if self.callback:
                self.callback('retry_level')

        buttons_container.add(retry_button)

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

        buttons_container.add(menu_button)

        right_spacer = UIBoxLayout(vertical=True)
        right_spacer.add(UILabel(text="", width=(self.width - 440) // 2, height=50))
        buttons_container.add(right_spacer)

        main_box.add(buttons_container)

        # Добавляем всё в менеджер
        self.ui_manager.add(main_box)

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

        # Советы по уровню
        if self.level_number == 1:
            tips.append("Начните с угольных буров и медных турелей")
        elif self.level_number == 2:
            tips.append("Используйте бронзовые турели для большей мощи")
        elif self.level_number == 3:
            tips.append("Стройте дальние турели и микросхемы")

        return tips[:3]  # Возвращаем не более 3 советов

    def on_draw(self):
        """Отрисовка окна"""
        self.clear()

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
        self.ui_manager.enable()

        self.background_color = arcade.color.DARK_BLUE
        self.setup_ui()

    def setup_ui(self):
        """Настройка интерфейса"""
        self.ui_manager.clear()

        # Основная вертикальная коробка с прокруткой
        main_box = UIBoxLayout(vertical=True, space_between=10)

        # Пустое пространство сверху
        main_box.add(UILabel(text="", height=30))

        # Заголовок
        title_label = UILabel(
            text="🏆 ИГРА ПРОЙДЕНА! 🏆",
            font_size=36,
            font_name="Kenney Future",
            text_color=arcade.color.GOLD,
            width=self.width - 100,
            align="center"
        )
        main_box.add(title_label)

        # Поздравление
        congrats_label = UILabel(
            text=f"Поздравляем, {self.username}!",
            font_size=24,
            text_color=arcade.color.LIGHT_GREEN,
            width=self.width - 100,
            align="center"
        )
        main_box.add(congrats_label)

        # Подзаголовок
        subtitle_label = UILabel(
            text="Вы прошли все 3 уровня игры!",
            font_size=20,
            text_color=arcade.color.LIGHT_BLUE,
            width=self.width - 100,
            align="center"
        )
        main_box.add(subtitle_label)

        # Пустое пространство
        main_box.add(UILabel(text="", height=20))

        # Общая статистика
        total_label = UILabel(
            text="📊 ОБЩАЯ СТАТИСТИКА:",
            font_size=22,
            text_color=arcade.color.LIGHT_BLUE,
            width=self.width - 100,
            align="center"
        )
        main_box.add(total_label)

        for text, color in [
            (f"🏆 Общий счет: {self.total_stats.get('total_score', 0)}", arcade.color.GOLD),
            (f"🎯 Всего врагов убито: {self.total_stats.get('total_enemies_killed', 0)}", arcade.color.RED),
            (f"⏱️ Общее время игры: {self.total_stats.get('total_play_time', 0):.1f} сек", arcade.color.CYAN),
            (f"🌊 Всего уровней пройдено: {self.total_stats.get('levels_completed', 0)}/3", arcade.color.BLUE),
            (f"🏭 Всего построено зданий: {self.total_stats.get('total_buildings', 0)}", arcade.color.BROWN),
            (f"🚁 Использовано дронов: {self.total_stats.get('total_drones', 0)}", arcade.color.SILVER)
        ]:
            if self.total_stats.get(text.split(':')[0].strip(), None) is not None or ':' in text:
                centered = UIBoxLayout(vertical=False)
                centered.add(UILabel(text="", width=(self.width - 400) // 2))
                centered.add(UILabel(
                    text=text,
                    font_size=18,
                    text_color=color,
                    width=400,
                    align="center"
                ))
                centered.add(UILabel(text="", width=(self.width - 400) // 2))
                main_box.add(centered)

        # Таблица глобальных рекордов
        main_box.add(UILabel(text="", height=30))

        records_label = UILabel(
            text="🏅 ГЛОБАЛЬНЫЕ РЕКОРДЫ:",
            font_size=22,
            text_color=arcade.color.GOLD,
            width=self.width - 100,
            align="center"
        )
        main_box.add(records_label)

        top_records = self.db.get_top_global_records(5)
        if top_records:
            for i, (record_username, score, levels, date_str) in enumerate(top_records, 1):
                medal = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣"][i - 1] if i <= 5 else f"{i}."

                # Создаем контейнер для строки таблицы
                row_container = UIBoxLayout(vertical=False, space_between=10)

                # Центрируем строку
                left_spacer = UILabel(text="", width=(self.width - 600) // 2)
                row_container.add(left_spacer)

                # Имя пользователя с медалью
                name_label = UILabel(
                    text=f"{medal} {record_username}",
                    font_size=16,
                    text_color=arcade.color.GOLD if i <= 3 else arcade.color.WHITE,
                    width=200,
                    align="left"
                )
                row_container.add(name_label)

                # Счет
                score_label = UILabel(
                    text=str(score),
                    font_size=16,
                    width=100,
                    align="center"
                )
                row_container.add(score_label)

                # Уровни
                levels_label = UILabel(
                    text=f"{levels}/3",
                    font_size=16,
                    width=100,
                    align="center"
                )
                row_container.add(levels_label)

                # Дата
                try:
                    date_obj = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
                    date_formatted = date_obj.strftime("%d.%m.%Y")
                except:
                    date_formatted = date_str

                date_label = UILabel(
                    text=date_formatted,
                    font_size=14,
                    text_color=arcade.color.LIGHT_GRAY,
                    width=120,
                    align="center"
                )
                row_container.add(date_label)

                right_spacer = UILabel(text="", width=(self.width - 600) // 2)
                row_container.add(right_spacer)

                main_box.add(row_container)

        # Пустое пространство перед кнопками
        main_box.add(UILabel(text="", height=50))

        # Кнопки действий
        buttons_container = UIBoxLayout(vertical=False, space_between=20)

        # Центрируем кнопки
        left_spacer = UIBoxLayout(vertical=True)
        left_spacer.add(UILabel(text="", width=(self.width - 640) // 2, height=50))
        buttons_container.add(left_spacer)

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

        buttons_container.add(new_game_button)

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

        buttons_container.add(menu_button)

        # Кнопка "Выход"
        exit_button = UIFlatButton(
            text="🚪 Выход",
            width=200,
            height=50
        )

        @exit_button.event("on_click")
        def on_exit(event):
            arcade.exit()

        buttons_container.add(exit_button)

        right_spacer = UIBoxLayout(vertical=True)
        right_spacer.add(UILabel(text="", width=(self.width - 640) // 2, height=50))
        buttons_container.add(right_spacer)

        main_box.add(buttons_container)

        # Добавляем всё в менеджер
        self.ui_manager.add(main_box)

        # Сохраняем глобальный рекорд
        if self.user_id:
            self.db.save_global_record(self.user_id, self.total_stats)
            # Разблокируем все уровни
            self.db.update_player_progress(self.user_id,
                                           3,  # Всего 3 уровня
                                           3)  # Разблокировать все 3 уровня

    def on_draw(self):
        """Отрисовка окна"""
        self.clear()

        # Рисуем праздничный фон
        self.draw_celebration_background()
        self.ui_manager.draw()

    def draw_celebration_background(self):
        """Рисуем праздничный фон с конфетти"""
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
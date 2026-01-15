# results_window.py
import arcade
import sqlite3
from arcade.gui import UIManager, UIBoxLayout, UIAnchorWidget
from arcade.gui.widgets import UILabel, UIInputText, UIFlatButton
from datetime import datetime
from database import ScoreDatabase


class ResultsWindow(arcade.Window):
    """Окно с результатами игры после прохождения всех уровней"""

    def __init__(self, width: int, height: int, title: str,
                 game_stats: Dict, return_callback=None):
        super().__init__(width, height, title)

        self.game_stats = game_stats
        self.return_callback = return_callback  # Функция для возврата в меню
        self.ui_manager = UIManager()
        self.score_db = ScoreDatabase()

        # Счетчик для анимации
        self.score_counter = 0
        self.total_score = game_stats.get('total_score', 0)
        self.counter_speed = max(1, self.total_score // 100)  # Скорость увеличения счетчика

        # Для ввода имени
        self.player_name = ""
        self.name_input_active = True

        self.setup_ui()

    def setup_ui(self):
        """Настройка интерфейса"""
        self.ui_manager.purge_ui_elements()

        # Фон
        self.background_color = arcade.color.DARK_SLATE_GRAY

        # Основной вертикальный контейнер
        v_box = UIBoxLayout(vertical=True, align="center", space_between=20)

        # Заголовок
        title_label = UILabel(
            text="ПОБЕДА!",
            font_size=48,
            font_name="Kenney Future",
            text_color=arcade.color.GOLD
        )
        v_box.add(title_label)

        # Подзаголовок
        subtitle_label = UILabel(
            text="Вы прошли все уровни!",
            font_size=24,
            text_color=arcade.color.LIGHT_GRAY
        )
        v_box.add(subtitle_label)

        # Отображение счета
        score_container = UIBoxLayout(vertical=False, align="center", space_between=50)

        # Левый блок - основной счет
        left_vbox = UIBoxLayout(vertical=True, align="left", space_between=10)

        left_vbox.add(UILabel(
            text="ВАШ СЧЕТ:",
            font_size=20,
            text_color=arcade.color.LIGHT_BLUE
        ))

        self.score_label = UILabel(
            text="0",
            font_size=36,
            text_color=arcade.color.GREEN
        )
        left_vbox.add(self.score_label)

        # Правый блок - детали счета
        right_vbox = UIBoxLayout(vertical=True, align="left", space_between=5)

        right_vbox.add(UILabel(
            text=f"Уничтожено врагов: {self.game_stats.get('enemies_killed', 0)}",
            font_size=16
        ))

        right_vbox.add(UILabel(
            text=f"Бонус за время: +{self.game_stats.get('time_bonus', 0)}",
            font_size=16
        ))

        # Разбивка по уровням
        for level, score in self.game_stats.get('level_scores', {}).items():
            right_vbox.add(UILabel(
                text=f"Уровень {level}: {score} очков",
                font_size=14,
                text_color=arcade.color.LIGHT_GRAY
            ))

        score_container.add(left_vbox)
        score_container.add(right_vbox)
        v_box.add(score_container)

        # Поле ввода имени (только если счет достаточно высокий)
        if self.total_score > 0:
            self.name_label = UILabel(
                text="Введите ваше имя для таблицы рекордов:",
                font_size=18
            )
            v_box.add(self.name_label)

            self.name_input = UIInputText(
                width=300,
                height=40,
                font_size=18,
                text_color=arcade.color.BLACK
            )
            v_box.add(self.name_input)

            # Кнопка сохранения
            save_button = UIFlatButton(
                text="Сохранить результат",
                width=200,
                height=40
            )

            @save_button.event("on_click")
            def on_click_save(event):
                self.save_score()

            v_box.add(save_button)

        # Таблица рекордов
        records_label = UILabel(
            text="ТАБЛИЦА РЕКОРДОВ",
            font_size=22,
            text_color=arcade.color.GOLD
        )
        v_box.add(records_label)

        self.records_container = UIBoxLayout(vertical=True, align="center", space_between=5)
        self.update_records_table()
        v_box.add(self.records_container)

        # Кнопки действий
        buttons_container = UIBoxLayout(vertical=False, align="center", space_between=20)

        # Кнопка "Играть снова"
        play_again_btn = UIFlatButton(
            text="Играть снова",
            width=180,
            height=40
        )

        @play_again_btn.event("on_click")
        def on_click_play_again(event):
            self.close()
            if self.return_callback:
                self.return_callback()

        # Кнопка "Выход"
        exit_btn = UIFlatButton(
            text="Выход",
            width=180,
            height=40
        )

        @exit_btn.event("on_click")
        def on_click_exit(event):
            arcade.exit()

        buttons_container.add(play_again_btn)
        buttons_container.add(exit_btn)
        v_box.add(buttons_container)

        # Добавляем все в менеджер
        self.ui_manager.add(UIAnchorWidget(
            anchor_x="center",
            anchor_y="center",
            child=v_box
        ))

    def update_records_table(self):
        """Обновление таблицы рекордов"""
        self.records_container.clear()

        top_scores = self.score_db.get_top_scores(10)

        if not top_scores:
            self.records_container.add(UILabel(
                text="Пока нет рекордов!",
                font_size=16
            ))
            return

        # Заголовок таблицы
        header = UIBoxLayout(vertical=False, align="center", space_between=20)
        header.add(UILabel(text="Игрок", width=150, font_size=14))
        header.add(UILabel(text="Счет", width=100, font_size=14))
        header.add(UILabel(text="Дата", width=150, font_size=14))
        self.records_container.add(header)

        # Данные таблицы
        for i, (name, score, kills, bonus, date_str) in enumerate(top_scores, 1):
            row = UIBoxLayout(vertical=False, align="center", space_between=20)

            # Место в рейтинге
            medal = ""
            if i == 1:
                medal = "🥇 "
            elif i == 2:
                medal = "🥈 "
            elif i == 3:
                medal = "🥉 "

            row.add(UILabel(
                text=f"{medal}{name}",
                width=150,
                font_size=14,
                text_color=arcade.color.GOLD if i <= 3 else arcade.color.WHITE
            ))

            row.add(UILabel(
                text=str(score),
                width=100,
                font_size=14
            ))

            # Форматируем дату
            date_obj = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
            date_formatted = date_obj.strftime("%d.%m.%Y")

            row.add(UILabel(
                text=date_formatted,
                width=150,
                font_size=14
            ))

            self.records_container.add(row)

    def save_score(self):
        """Сохранение результата в базу данных"""
        if not self.name_input.text or len(self.name_input.text.strip()) == 0:
            return

        player_name = self.name_input.text.strip()[:50]  # Ограничиваем длину

        self.score_db.save_score(
            player_name=player_name,
            total_score=self.total_score,
            level_scores=self.game_stats.get('level_scores', {}),
            enemies_killed=self.game_stats.get('enemies_killed', 0),
            time_bonus=self.game_stats.get('time_bonus', 0),
            stats=self.game_stats.get('detailed_stats', {})
        )

        # Обновляем таблицу рекордов
        self.update_records_table()

        # Отключаем поле ввода
        self.name_input_active = False
        self.name_label.text = "Результат сохранен!"

    def on_update(self, delta_time: float):
        """Обновление анимации счетчика очков"""
        if self.score_counter < self.total_score:
            increment = min(self.counter_speed, self.total_score - self.score_counter)
            self.score_counter += increment
            self.score_label.text = str(int(self.score_counter))

    def on_draw(self):
        """Отрисовка окна"""
        self.clear()

        # Рисуем звездное небо на фоне
        self.draw_star_background()

        # Рисуем UI
        self.ui_manager.draw()

    def draw_star_background(self):
        """Рисуем звездное небо"""
        arcade.draw_lrtb_rectangle_filled(
            0, self.width, self.height, 0,
            arcade.color.DARK_BLUE
        )

        # Простые звезды
        for i in range(50):
            x = (i * 37) % self.width
            y = (i * 23) % self.height
            size = 1 + (i % 3)
            arcade.draw_circle_filled(x, y, size, arcade.color.WHITE)

    def on_key_press(self, symbol: int, modifiers: int):
        """Обработка нажатий клавиш"""
        if symbol == arcade.key.ESCAPE:
            arcade.exit()

    def on_close(self):
        """Закрытие окна"""
        self.ui_manager.unregister_handlers()
        super().close()
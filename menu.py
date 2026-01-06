# menu.py
import arcade
from arcade.gui import UIManager
from typing import Dict, Any
from game import MyGame


class StartMenuWindow(arcade.Window):
    """Стартовое меню игры - простой интерфейс для запуска игры"""

    def __init__(self, width: int, height: int, title: str):
        """
        Инициализация стартового меню

        Параметры:
        width: int - ширина окна
        height: int - высота окна
        title: str - заголовок окна

        Атрибуты:
        self.ui_manager: UIManager - менеджер интерфейса
        self.width/height: int - размеры окна
        self.title: str - заголовок
        """
        super().__init__(width, height, title)
        self.ui_manager = UIManager()
        self.setup_ui()

    def setup_ui(self):
        pass
        """
        Настройка интерфейса стартового меню

        Создает UI элементы:
        - Кнопка "Начать проходить первый уровень"
        - Кнопка "Выход"
        - Заголовок и фон

        Логика:
        - Создает вертикальную панель по центру экрана
        - Добавляет кнопки с обработчиками нажатий
        - Устанавливает стиль и позиционирование
        """

    def start_game(self):
        pass
        """
        Запуск основной игры

        Логика:
        - Закрывает меню
        - Создает окно игры с картой level1.json
        - Инициализирует игру через метод setup()
        - Запускает игровой цикл
        """

    def on_draw(self):
        pass
        """
        Отрисовка стартового меню

        Логика:
        - Очищает экран
        - Рисует фон
        - Рисует UI элементы через ui_manager
        - Рисует заголовок и кнопки
        """

    def on_close(self):
        pass
        """
        Обработка закрытия окна

        Логика:
        - Вызывает базовый метод on_close()
        - Завершает приложение через arcade.exit()
        """
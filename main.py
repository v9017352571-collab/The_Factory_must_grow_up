# main.py
import arcade
from database import init_database
from menu import StartMenuWindow


def main():
    """
    Точка входа в игру

    Задачи:
    - Создает окно стартового меню
    - Запускает игровой цикл
    - Обрабатывает закрытие приложения

    Особенности:
    - Размер окна: 800x600 пикселей
    - Заголовок: "Заводы и Тауэр Дефенс"
    - Автоматический выход при закрытии окна
    """

    window = StartMenuWindow(800, 600, "Заводы и Тауэр Дефенс")
    window.set_update_rate(1 / 60)
    arcade.run()


if __name__ == "__main__":
    main()
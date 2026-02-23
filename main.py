import arcade
from menu import StartMenuView

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Заводы и Тауэр Дефенс"


def main():
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    start_view = StartMenuView()
    window.show_view(start_view)
    arcade.run()


if __name__ == "__main__":
    main()
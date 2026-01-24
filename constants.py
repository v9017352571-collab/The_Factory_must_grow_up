# constants.py
"""
Константы игры с загрузкой из базы данных уровней

Этот файл загружает данные текущего уровня из SQLite базы данных.
Все константы инициализируются при импорте файла.
"""
level = 1
import arcade
import sqlite3


def get_voln_data(level):
    conn = sqlite3.connect('level.sqlite')
    cursor = conn.cursor()
    cursor.execute("SELECT voln, json FROM Уровни WHERE level = ?", (level,))
    result = cursor.fetchall()[0]
    conn.close()

    # Разбиваем на строки по \r\n
    lines = result[0].split('\r\n')

    # Разбиваем каждую строку на элементы по запятым
    result_list = []
    for line in lines:
        # Просто делим по запятым и убираем лишние пробелы
        items = [item for item in line.split(',')]
        result_list.append(items)

    return result_list, result[1]


WAVES, JSON = get_voln_data(level)

# Размеры и масштабы
T_SIZE = 80  # пикселей на клетку
SPRITE_SCALE = 0.25  # масштаб для 32px спрайтов (становится 16px)

# Ресурсы в игре
RESOURCES = ["Медь", "Олово", "Уголь", "Бронза", "Кремний", "Боеприпасы"]

# Скорости объектов
DRONE_SPEED = 1.0  # блоков в секунду (1 блок = 16 пикселей)
PLAYER_SPEED = 1.0  # блоков в секунду

# Дистанции взаимодействия
PLAYER_PICKUP_DISTANCE = 3 * T_SIZE  # игрок может брать ресурсы на расстоянии 3 блоков
PLAYER_DROP_DISTANCE = 3 * T_SIZE  # игрок может класть ресурсы на расстоянии 3 блоков
DRONE_PICKUP_DISTANCE = 1 * T_SIZE  # дроны могут брать ресурсы на расстоянии 1 блока
DRONE_DROP_DISTANCE = 1 * T_SIZE  # дроны могут класть ресурсы на расстоянии 1 блока

# Горячие клавиши для постройки
# Здоровье зданий (кроме ядра)
BUILDING_HP = {
    "Дрон-станция": 5,
    "Угольный бур": 5,
    "Электрический бур": 5,
    "Печь для бронзы": 5,
    "Кремниевая печь": 5,
    "Завод микросхем": 5,
    "Завод боеприпасов": 5,
    "Медная турель": 5,
    "Бронзовая турель": 10,
    "Дальняя турель": 5
}

TEXTYRE = {
    "Медь": "Изображения\Остальное\Ресурсы\Медь.png",
    "Олово": "Изображения\Остальное\Ресурсы\Олово.png",
    "Уголь": "Изображения\Остальное\Ресурсы\Уголь.png",
    "Бронза": "Изображения\Остальное\Ресурсы\Бронза.png",
    "Кремний": "Изображения\Остальное\Ресурсы\Кремний.png",
    "Боеприпасы": "Изображения\Остальное\Ресурсы\Боеприпасы.png",

}

DRONE_RECOVERY_COST = "all_resources"  # специальная константа для обозначения вычета всех ресурсов

players = arcade.SpriteList()
buildings = arcade.SpriteList()
bugs = arcade.SpriteList()
good_bullet = arcade.SpriteList()
bad_bullet = arcade.SpriteList()
CAMERA_LERP = 0.12


from buildings import ElectricDrill, BronzeFurnace, SiliconFurnace, AmmoFactory, CopperTurret,\
    BronzeTurret, LongRangeTurret
from enemies import (Bug, Beetle, ArmoredBeetle, SpittingBeetle,
                     DominicTorettoBeetle, HarkerBeetle)

BUILDING_KEYS = {
    arcade.key.KEY_1: ElectricDrill,
    arcade.key.KEY_2: BronzeFurnace,
    arcade.key.KEY_3: SiliconFurnace,
    arcade.key.KEY_4: AmmoFactory,
    arcade.key.KEY_5: CopperTurret,
    arcade.key.KEY_6: BronzeTurret,
    arcade.key.KEY_7: LongRangeTurret
}
BAGS = {
    "Обычный жук": Beetle,
    "Броненосец": ArmoredBeetle,
    "Жук-плевок": SpittingBeetle,
    "Жук Доминико Торетто": DominicTorettoBeetle,
    "Жук-харкатель": HarkerBeetle
        }

MUSIC_MENU = arcade.load_sound('OST\Меню\ДляМеню.mp3')
MUSIC_ATTACKS1 = arcade.load_sound('OST\Атака\Атака1.mp3')
MUSIC_ATTACKS2 = arcade.load_sound("OST\Атака\Атака2.mp3")
MUSIC_ATTACKS3 = arcade.load_sound("OST\Атака\Атака3.mp3")
MUSIC_UNITED1 = arcade.load_sound("OST\Обычная\Обычная1.mp3")
MUSIC_UNITED2 = arcade.load_sound("OST\Обычная\Обычная2.mp3")
MUSIC_UNITED3 = arcade.load_sound("OST\Обычная\Обычная3.mp3")
HIT = [arcade.load_sound("Стрельба\Поподание\п1.mp3"), arcade.load_sound("Стрельба\Поподание\п2.mp3"),
       arcade.load_sound("Стрельба\Поподание\п3.mp3"), arcade.load_sound("Стрельба\Поподание\п4.mp3"),
       arcade.load_sound("Стрельба\Поподание\п5.mp3"), arcade.load_sound("Стрельба\Поподание\п6.mp3"),
       arcade.load_sound("Стрельба\Поподание\п7.mp3")]
SOUND_COPPER_TURRET = [arcade.load_sound("Стрельба\Турель\Медная\т1.mp3"),
                       arcade.load_sound("Стрельба\Турель\Медная\т2.mp3"),
                       arcade.load_sound("Стрельба\Турель\Медная\т3.mp3")]
SOUND_BRONZE_TURRET = [arcade.load_sound("Стрельба\Турель\Бронзавая\т1.mp3"),
                       arcade.load_sound("Стрельба\Турель\Бронзавая\т2.mp3")]
SOUND_LONG_BARRELED_TURRET = [arcade.load_sound("Стрельба\Турель\Длинноствольная\т1.mp3"),
                       arcade.load_sound("Стрельба\Турель\Длинноствольная\т2.mp3"),
                       arcade.load_sound("Стрельба\Турель\Длинноствольная\т3.mp3")]
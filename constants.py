# constants.py
from enemies import (Bug, Beetle, ArmoredBeetle, SpittingBeetle,
                     DominicTorettoBeetle, HarkerBeetle)
"""
Константы игры с загрузкой из базы данных уровней

Этот файл загружает данные текущего уровня из SQLite базы данных.
Все константы инициализируются при импорте файла.
"""
import sqlite3
import arcade

# === ПОДКЛЮЧЕНИЕ К БАЗЕ ДАННЫХ ===
DB_PATH = "level.sqlite"  # путь к файлу базы данных
CURRENT_LEVEL = 1  # текущий уровень для загрузки (можно изменить, но потом)
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# === ЗАГРУЗКА ДАННЫХ УРОВНЯ ===
cursor.execute("SELECT voln, json FROM Уровни WHERE level = ?", (CURRENT_LEVEL,))
row = cursor.fetchone()

if row:
    # === ЗАГРУЗКА ВОЛН ===
    voln_text = row[0]  # текстовое представление волн
    try:
        # Безопасное преобразование текста в Python список
        WAVES = exec(voln_text)
    except (SyntaxError, ValueError) as e:
        print(f"Ошибка преобразования волн: {e}")
        # Базовые волны для отладки
        WAVES = [
            [180, ["Обычный жук", "Обычный жук"]],
            [120, ["Обычный жук", "Броненосец", "Обычный жук"]],]

# === КАРТА ===

#JSON = row[2]

# === ОСНОВНЫЕ КОНСТАНТЫ ===

# Размеры и масштабы
TILE_SIZE = 16  # пикселей на клетку
SPRITE_SCALE = 0.5  # масштаб для 32px спрайтов (становится 16px)

# Ресурсы в игре
RESOURCES = ["Медь", "Олово", "Уголь", "Бронза", "Кремний", "Боеприпасы"]

# Скорости объектов
DRONE_SPEED = 1.0  # блоков в секунду (1 блок = 16 пикселей)
PLAYER_SPEED = 1.0  # блоков в секунду

# Дистанции взаимодействия
PLAYER_PICKUP_DISTANCE = 3 * TILE_SIZE  # игрок может брать ресурсы на расстоянии 3 блоков
PLAYER_DROP_DISTANCE = 3 * TILE_SIZE  # игрок может класть ресурсы на расстоянии 3 блоков
DRONE_PICKUP_DISTANCE = 1 * TILE_SIZE  # дроны могут брать ресурсы на расстоянии 1 блока
DRONE_DROP_DISTANCE = 1 * TILE_SIZE  # дроны могут класть ресурсы на расстоянии 1 блока

# Горячие клавиши для постройки
BUILDING_KEYS = {
    arcade.key.KEY_1: "Дрон-станция",
    arcade.key.KEY_2: "Угольный бур",
    arcade.key.KEY_3: "Электрический бур",
    arcade.key.KEY_4: "Печь для бронзы",
    arcade.key.KEY_5: "Кремниевая печь",
    arcade.key.KEY_6: "Завод микросхем",
    arcade.key.KEY_7: "Завод боеприпасов",
    arcade.key.KEY_8: "Медная турель",
    arcade.key.KEY_9: "Бронзовая турель",
    arcade.key.KEY_0: "Дальняя турель"
}

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
BAGS = {
    "Обычный жук": Beetle,
    "Броненосец": ArmoredBeetle,
    "Жук-плевок": SpittingBeetle,
    "Жук Доминико Торетто": DominicTorettoBeetle,
    "Жук-харкатель": HarkerBeetle
        }
# Дополнительные константы для дронов
DRONE_RECOVERY_COST = "all_resources"  # специальная константа для обозначения вычета всех ресурсов

players = arcade.SpriteList()
buildings = arcade.SpriteList()
bugs = arcade.SpriteList()
CAMERA_LERP = 0.12
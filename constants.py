# constants.py
"""
Константы игры с данными уровней.
"""
import sqlite3
import os
import zipfile
import shutil
import json
from buildings import Building, ElectricDrill, BronzeFurnace, SiliconFurnace, AmmoFactory, CopperTurret,\
    BronzeTurret, LongRangeTurret
from enemies import (Bug, Beetle, ArmoredBeetle, SpittingBeetle,
                     DominicTorettoBeetle, HarkerBeetle)
import arcade

# --- Данные уровней ---
LEVELS = {
    1: {
        "waves": [
            ["Обычный жук", "Обычный жук"],
            ["Обычный жук", "Броненосец", "Обычный жук"]
        ],
        "map": "level1.json"  # или полный путь к файлу карты
    },
    2: {
        "waves": [
            ["Обычный жук", "Жук-плевок"],
            ["Броненосец", "Броненосец", "Обычный жук"],
            ["Жук-харкатель"]
        ],
        "map": "level2.json"
    },
    3: {
        "waves": [
            ["Жук-плевок", "Жук-плевок"],
            ["Броненосец", "Жук-харкатель", "Обычный жук"],
            ["Доминико Торетто"],
            ["Жук-харкатель", "Жук-харкатель", "Броненосец"]
        ],
        "map": "level3.json"
    }
}

# Номер текущего уровня по умолчанию (можно изменить вручную)
CURRENT_LEVEL = 1

# Размеры и масштабы
T_SIZE = 80  # пикселей на клетку
SPRITE_SCALE = 0.25  # масштаб для 32px спрайтов (становится 16px)

# Ресурсы в игре
RESOURCES = ["Медь", "Олово", "Уголь", "Бронза", "Кремний", "Боеприпасы"]

# Скорости объектов
DRONE_SPEED = 1.0  # блоков в секунду (1 блок = 16 пикселей)
PLAYER_SPEED = 1.0  # блоков в секунду

# Дистанции взаимодействия
PLAYER_PICKUP_DISTANCE = 3 * T_SIZE
PLAYER_DROP_DISTANCE = 3 * T_SIZE
DRONE_PICKUP_DISTANCE = 1 * T_SIZE
DRONE_DROP_DISTANCE = 1 * T_SIZE

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
    "Медь": "Изображения/Остальное/Ресурсы/Медь.png",
    "Олово": "Изображения/Остальное/Ресурсы/Олово.png",
    "Уголь": "Изображения/Остальное/Ресурсы/Уголь.png",
    "Бронза": "Изображения/Остальное/Ресурсы/Бронза.png",
    "Кремний": "Изображения/Остальное/Ресурсы/Кремний.png",
    "Боеприпасы": "Изображения/Остальное/Ресурсы/Боеприпасы.png",
}

DRONE_RECOVERY_COST = "all_resources"
CAMERA_LERP = 0.12

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

# --- Работа с ZIP архивом звуков (без изменений) ---
ZIP_FILENAME = "mp.zip"
EXTRACTED_DIR = "extracted_sounds"

def cleanup_directory():
    if os.path.exists(EXTRACTED_DIR):
        try:
            shutil.rmtree(EXTRACTED_DIR)
            print(f"Директория {EXTRACTED_DIR} очищена")
        except Exception as e:
            print(f"Ошибка при очистке директории: {e}")

cleanup_directory()
os.makedirs(EXTRACTED_DIR, exist_ok=True)

if not os.path.exists(ZIP_FILENAME):
    print(f"Ошибка: Файл {ZIP_FILENAME} не найден!")
    print(f"Текущая директория: {os.getcwd()}")
    exit(1)

try:
    with zipfile.ZipFile(ZIP_FILENAME, 'r') as zip_ref:
        zip_ref.extractall(EXTRACTED_DIR)
    print(f"Файлы успешно распакованы в: {EXTRACTED_DIR}")
except Exception as e:
    print(f"Ошибка при распаковке {ZIP_FILENAME}: {e}")
    exit(1)

MP_FOLDER = os.path.join(EXTRACTED_DIR, "mp")

def load_sound_from_mp(relative_path):
    full_path = os.path.join(MP_FOLDER, relative_path)
    full_path = os.path.normpath(full_path)
    if os.path.exists(full_path):
        try:
            return arcade.load_sound(full_path)
        except Exception as e:
            print(f"Ошибка при загрузке звука {full_path}: {e}")
            return None
    else:
        print(f"Файл не найден: {full_path}")
        return None

print("\nЗагрузка звуков с реальными именами файлов...")
MUSIC_MENU = load_sound_from_mp('OST/îÑ¡ε/ä½∩îÑ¡ε.mp3')
MUSIC_ATTACKS1 = load_sound_from_mp('OST/ÇΓá¬á/ÇΓá¬á1.mp3')
MUSIC_ATTACKS2 = load_sound_from_mp('OST/ÇΓá¬á/ÇΓá¬á2.mp3')
MUSIC_ATTACKS3 = load_sound_from_mp('OST/ÇΓá¬á/ÇΓá¬á3.mp3')
MUSIC_UNITED1 = load_sound_from_mp('OST/Äíδτ¡á∩/Äíδτ¡á∩1.mp3')
MUSIC_UNITED2 = load_sound_from_mp('OST/Äíδτ¡á∩/Äíδτ¡á∩2.mp3')
MUSIC_UNITED3 = load_sound_from_mp('OST/Äíδτ¡á∩/Äíδτ¡á∩3.mp3')

HIT = [
    load_sound_from_mp('æΓαÑ½∞íá/Å«»«ñá¡¿Ñ/»1.mp3'),
    load_sound_from_mp('æΓαÑ½∞íá/Å«»«ñá¡¿Ñ/»2.mp3'),
    load_sound_from_mp('æΓαÑ½∞íá/Å«»«ñá¡¿Ñ/»3.mp3'),
    load_sound_from_mp('æΓαÑ½∞íá/Å«»«ñá¡¿Ñ/»4.mp3'),
    load_sound_from_mp('æΓαÑ½∞íá/Å«»«ñá¡¿Ñ/»5.mp3'),
    load_sound_from_mp('æΓαÑ½∞íá/Å«»«ñá¡¿Ñ/»6.mp3'),
    load_sound_from_mp('æΓαÑ½∞íá/Å«»«ñá¡¿Ñ/»7.mp3')
]

SOUND_COPPER_TURRET = [
    load_sound_from_mp('æΓαÑ½∞íá/ÆπαÑ½∞/îÑñ¡á∩/Γ1.mp3'),
    load_sound_from_mp('æΓαÑ½∞íá/ÆπαÑ½∞/îÑñ¡á∩/Γ2.mp3'),
    load_sound_from_mp('æΓαÑ½∞íá/ÆπαÑ½∞/îÑñ¡á∩/Γ3.mp3')
]

SOUND_BRONZE_TURRET = [
    load_sound_from_mp('æΓαÑ½∞íá/ÆπαÑ½∞/üα«¡ºáóá∩/Γ1.mp3'),
    load_sound_from_mp('æΓαÑ½∞íá/ÆπαÑ½∞/üα«¡ºáóá∩/Γ2.mp3')
]

SOUND_LONG_BARRELED_TURRET = [
    load_sound_from_mp('æΓαÑ½∞íá/ÆπαÑ½∞/ä½¿¡¡«ßΓó«½∞¡á∩/Γ1.mp3'),
    load_sound_from_mp('æΓαÑ½∞íá/ÆπαÑ½∞/ä½¿¡¡«ßΓó«½∞¡á∩/Γ2.mp3'),
    load_sound_from_mp('æΓαÑ½∞íá/ÆπαÑ½∞/ä½¿¡¡«ßΓó«½∞¡á∩/Γ3.mp3')
]

print("\nЗагрузка звуков завершена!")

import atexit
atexit.register(cleanup_directory)
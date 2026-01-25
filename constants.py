# constants.py
"""
Константы игры с загрузкой из базы данных уровней

Этот файл загружает данные текущего уровня из SQLite базы данных.
Все константы инициализируются при импорте файла.
"""
level_name = '1' # потом будет импорт
import sqlite3
import os
import zipfile
import shutil
import json
from buildings import ElectricDrill, BronzeFurnace, SiliconFurnace, AmmoFactory, CopperTurret,\
    BronzeTurret, LongRangeTurret
from enemies import (Bug, Beetle, ArmoredBeetle, SpittingBeetle,
                     DominicTorettoBeetle, HarkerBeetle)
import arcade
import importlib



# def get_voln_data(level):
#     conn = sqlite3.connect('level.sqlite')
#     cursor = conn.cursor()
#     cursor.execute("SELECT voln, json FROM Уровни WHERE id = ?", (level,))
#     result = cursor.fetchall()[0]
#     conn.close()
#
#     # Разбиваем на строки по \r\n
#     lines = result.split('\r\n')
#
#     # Разбиваем каждую строку на элементы по запятым
#     result_list = []
#     for line in lines:
#         # Просто делим по запятым и убираем лишние пробелы
#         items = [item for item in line.split(',')]
#         result_list.append(items)
#
#     return result_list, result[1]
#
#
# WAVES, JSON = get_voln_data(level)

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


def save_level_to_db(name: str, voln, map_json,
                     spr_list_dict) -> bool:
    """
    Сохраняет уровень в базу данных level.sqlite.

    Параметры:
    name (str): Имя уровня
    voln (List[List[str]]): Список списков для поля "voln"
    map_json (Dict[str, Any]): Данные карты в формате JSON
    spr_list_dict (Dict[str, arcade.SpriteList]): Словарь с SpriteList для разных типов объектов

    Формат spr_list_dict должен содержать:
    {
        'players': arcade.SpriteList(),  # Список игроков
        'buildings': arcade.SpriteList(), # Список зданий
        'bugs': arcade.SpriteList(),     # Список насекомых/врагов
        'good_bullet': arcade.SpriteList(), # Список хороших пуль
        'bad_bullet': arcade.SpriteList()   # Список плохих пуль
    }

    Возвращает:
    bool: True при успешном сохранении, False при ошибке
    """
    try:
        # === ШАГ 1: Подготовка данных для сохранения ===

        # Преобразуем voln (список списков) в строку
        # Формат: каждая внутренняя строка объединяется через запятую,
        # а строки разделаются через \r\n
        voln_str = '\r\n'.join([','.join(str(item) for item in row) for row in voln])

        # Преобразуем карту в JSON-строку
        map_json_str = json.dumps(map_json, ensure_ascii=False)

        # Подготовка players_bugs_buildings
        # Создаем словарь с сериализованными SpriteList
        players_bugs_buildings = {
            'players': serialize_sprite_list(spr_list_dict.get('players', arcade.SpriteList())),
            'buildings': serialize_sprite_list(spr_list_dict.get('buildings', arcade.SpriteList())),
            'bugs': serialize_sprite_list(spr_list_dict.get('bugs', arcade.SpriteList())),
            'good_bullet': serialize_sprite_list(spr_list_dict.get('good_bullet', arcade.SpriteList())),
            'bad_bullet': serialize_sprite_list(spr_list_dict.get('bad_bullet', arcade.SpriteList()))
        }

        # Преобразуем весь словарь в JSON-строку
        players_bugs_buildings_str = json.dumps(players_bugs_buildings, ensure_ascii=False)

        # === ШАГ 2: Подключение к базе данных ===
        conn = sqlite3.connect('level.sqlite')
        cursor = conn.cursor()

        # === ШАГ 3: Подготовка SQL запроса ===
        # Используем INSERT OR REPLACE для обновления существующих записей
        sql = """
        INSERT OR REPLACE INTO levels (name, voln, json, players_bugs_buildings)
        VALUES (?, ?, ?, ?)
        """

        # === ШАГ 4: Выполнение запроса ===
        # Так как поля объявлены как BLOB, но мы храним JSON-строки,
        # преобразуем строки в байты
        cursor.execute(sql, (
            name,
            voln_str,
            map_json_str.encode('utf-8'),  # Преобразуем в bytes для BLOB
            players_bugs_buildings_str.encode('utf-8')  # Преобразуем в bytes для BLOB
        ))

        # === ШАГ 5: Фиксация изменений ===
        conn.commit()

        # === ШАГ 6: Закрытие соединения ===
        conn.close()

        print(f"✅ Уровень '{name}' успешно сохранен в базу данных")
        print(f"   ├─ voln: {len(voln)} строк")
        print(f"   ├─ карта: {len(map_json_str)} символов")
        print(f"   └─ спрайты: players={len(spr_list_dict.get('players', []))}, "
              f"buildings={len(spr_list_dict.get('buildings', []))}, "
              f"bugs={len(spr_list_dict.get('bugs', []))}")

        return True

    except sqlite3.Error as e:
        print(f"❌ Ошибка SQLite при сохранении уровня '{name}': {e}")
        return False
    except Exception as e:
        print(f"❌ Неожиданная ошибка при сохранении уровня '{name}': {e}")
        return False

def serialize_sprite_list(sprite_list: arcade.SpriteList) -> str:
    """
    Преобразует arcade.SpriteList в JSON-строку.

    Эта функция автоматически собирает все публичные атрибуты спрайтов,
    которые можно сериализовать в JSON.

    Параметры:
    sprite_list (arcade.SpriteList): Список спрайтов для сериализации

    Возвращает:
    str: JSON-строка с данными всех спрайтов
    """
    sprites_data = []

    for sprite in sprite_list:
        # Определяем тип спрайта для последующего воссоздания
        module_name = sprite.__class__.__module__
        class_name = sprite.__class__.__name__

        # Собираем атрибуты для сохранения
        attributes = {}
        for attr_name in dir(sprite):
            # Пропускаем приватные атрибуты и системные методы
            if (attr_name.startswith('_') or
                    attr_name in ['draw', 'update', 'kill', 'remove_from_sprite_lists']):
                continue

            attr_value = getattr(sprite, attr_name)

            # Пропускаем методы и функции
            if callable(attr_value):
                continue

            # Пропускаем сложные объекты arcade
            if isinstance(attr_value, (arcade.SpriteList, arcade.Sprite, arcade.Texture)):
                continue

            # Проверяем, можно ли сериализовать в JSON
            try:
                json.dumps(attr_value)
                attributes[attr_name] = attr_value
            except TypeError:
                continue

        sprites_data.append({
            'module': module_name,
            'class': class_name,
            'attributes': attributes
        })

    # Возвращаем JSON-строку
    return json.dumps({
        'sprites': sprites_data,
        'count': len(sprite_list)
    }, ensure_ascii=False)

def deserialize_sprite_list(json_str: str) -> arcade.SpriteList:
    """
    Преобразует JSON-строку обратно в arcade.SpriteList.

    Эта функция воссоздает спрайты на основе сохраненных данных,
    динамически импортируя нужные классы.

    Параметры:
    json_str (str): JSON-строка с данными спрайтов

    Возвращает:
    arcade.SpriteList: Восстановленный список спрайтов
    """
    try:
        data = json.loads(json_str)
        sprite_list = arcade.SpriteList()

        for sprite_data in data['sprites']:
            module_name = sprite_data['module']
            class_name = sprite_data['class']
            attributes = sprite_data['attributes']

            try:
                # Динамически импортируем модуль и класс
                module = importlib.import_module(module_name)
                sprite_class = getattr(module, class_name)

                # Создаем экземпляр спрайта
                # Важно: конструктор не должен требовать обязательных параметров!
                sprite = sprite_class()

                # Восстанавливаем атрибуты
                for attr_name, attr_value in attributes.items():
                    # Пропускаем внутренние атрибуты arcade
                    if attr_name in ['textures', 'texture', 'sprite_lists', 'bottom', 'top', 'left', 'right']:
                        continue

                    try:
                        setattr(sprite, attr_name, attr_value)
                    except (AttributeError, TypeError):
                        continue

                # Обновляем позицию (на случай, если arcade изменил внутреннюю логику)
                if hasattr(sprite, 'center_x') and hasattr(sprite, 'center_y'):
                    sprite.position = (sprite.center_x, sprite.center_y)

                sprite_list.append(sprite)

            except (ImportError, AttributeError, TypeError, Exception) as e:
                print(f"⚠️ Ошибка при восстановлении спрайта {class_name}: {e}")
                continue

        return sprite_list

    except (json.JSONDecodeError, KeyError, Exception) as e:
        print(f"❌ Ошибка при десериализации SpriteList: {e}")
        return arcade.SpriteList()

def load_level_from_db(name: str):
    """
    Загружает уровень из базы данных level.sqlite по имени.

    Параметры:
    name (str): Имя уровня для загрузки

    Возвращает:
    Tuple[List[List[str]], Dict[str, Any], Dict[str, arcade.SpriteList]] | None:
        - WALES: voln преобразованный в список списков
        - map_json: карта в формате JSON (словарь)
        - players_bugs_buildings: словарь со SpriteList для разных типов объектов
        или None, если уровень не найден

    Структура возвращаемого словаря players_bugs_buildings:
    {
        'players': arcade.SpriteList(),  # Список игроков
        'buildings': arcade.SpriteList(), # Список зданий
        'bugs': arcade.SpriteList(),     # Список насекомых/врагов
        'good_bullet': arcade.SpriteList(), # Список хороших пуль
        'bad_bullet': arcade.SpriteList()   # Список плохих пуль
    }
    """
    try:
        # === ШАГ 1: Подключение к базе данных ===
        conn = sqlite3.connect('level.sqlite')
        cursor = conn.cursor()

        # === ШАГ 2: Выполнение запроса ===
        cursor.execute('SELECT voln, json, players_bugs_buildings FROM levels WHERE name = ?', (name,))
        result = cursor.fetchone()

        # === ШАГ 3: Проверка результата ===
        if result is None:
            print(f"⚠️ Уровень '{name}' не найден в базе данных")
            conn.close()
            return None

        voln_str, map_json_blob, players_bugs_buildings_blob = result

        # === ШАГ 4: Преобразование данных ===

        # --- Преобразование voln_str в WALES (список списков) ---
        WALES = []
        if voln_str:
            # Разбиваем строку на строки по \r\n
            lines = voln_str.split('\r\n')
            for line in lines:
                if line.strip():  # Пропускаем пустые строки
                    # Разбиваем каждую строку на элементы по запятым
                    items = [item.strip() for item in line.split(',') if item.strip()]
                    WALES.append(items)

        # --- Преобразование map_json_blob в словарь ---
        if isinstance(map_json_blob, bytes):
            map_json_str = map_json_blob.decode('utf-8')
        else:
            map_json_str = str(map_json_blob)

        try:
            map_json = json.loads(map_json_str)
        except json.JSONDecodeError:
            print(f"⚠️ Ошибка при декодировании JSON карты для уровня '{name}'")
            map_json = {}

        # --- Преобразование players_bugs_buildings_blob в словарь со SpriteList ---
        if isinstance(players_bugs_buildings_blob, bytes):
            players_bugs_buildings_str = players_bugs_buildings_blob.decode('utf-8')
        else:
            players_bugs_buildings_str = str(players_bugs_buildings_blob)

        try:
            players_bugs_buildings_data = json.loads(players_bugs_buildings_str)

            # Создаем словарь для SpriteList
            players_bugs_buildings = {
                'players': deserialize_sprite_list(players_bugs_buildings_data.get('players', '[]')),
                'buildings': deserialize_sprite_list(players_bugs_buildings_data.get('buildings', '[]')),
                'bugs': deserialize_sprite_list(players_bugs_buildings_data.get('bugs', '[]')),
                'good_bullet': deserialize_sprite_list(players_bugs_buildings_data.get('good_bullet', '[]')),
                'bad_bullet': deserialize_sprite_list(players_bugs_buildings_data.get('bad_bullet', '[]'))
            }

            # Выводим отладочную информацию
            print(f"✅ Загружен уровень '{name}'")
            print(f"   ├─ WALES: {len(WALES)} строк, {sum(len(row) for row in WALES)} элементов")
            print(f"   ├─ карта: {len(map_json)} ключей")
            print(f"   └─ спрайты: players={len(players_bugs_buildings['players'])}, "
                  f"buildings={len(players_bugs_buildings['buildings'])}, "
                  f"bugs={len(players_bugs_buildings['bugs'])}")

        except (json.JSONDecodeError, KeyError, Exception) as e:
            print(f"⚠️ Ошибка при загрузке спрайтов для уровня '{name}': {e}")
            # Создаем пустые SpriteList при ошибке
            players_bugs_buildings = {
                'players': arcade.SpriteList(),
                'buildings': arcade.SpriteList(),
                'bugs': arcade.SpriteList(),
                'good_bullet': arcade.SpriteList(),
                'bad_bullet': arcade.SpriteList()
            }

        # === ШАГ 5: Закрытие соединения ===
        conn.close()

        return WALES, map_json, players_bugs_buildings

    except sqlite3.Error as e:
        print(f"❌ Ошибка SQLite при загрузке уровня '{name}': {e}")
        return None
    except Exception as e:
        print(f"❌ Неожиданная ошибка при загрузке уровня '{name}': {e}")
        return None


WAVES, JSON, s = load_level_from_db(level_name)
players = s['players']
buildings = s['buildings']
bugs = s['bugs']
good_bullet = s['good_bullet']
bad_bullet = s['bad_bullet']
print(load_level_from_db(level_name))






# Имя zip-файла
ZIP_FILENAME = "mp.zip"

# Директория для распаковки
EXTRACTED_DIR = "extracted_sounds"
# Функция для очистки директории
def cleanup_directory():
    if os.path.exists(EXTRACTED_DIR):
        try:
            shutil.rmtree(EXTRACTED_DIR)
            print(f"Директория {EXTRACTED_DIR} очищена")
        except Exception as e:
            print(f"Ошибка при очистке директории: {e}")


# Очищаем старую директорию перед распаковкой
cleanup_directory()
os.makedirs(EXTRACTED_DIR, exist_ok=True)

# Проверяем наличие zip-файла
if not os.path.exists(ZIP_FILENAME):
    print(f"Ошибка: Файл {ZIP_FILENAME} не найден!")
    print(f"Текущая директория: {os.getcwd()}")
    exit(1)

# Распаковываем zip-файл
try:
    with zipfile.ZipFile(ZIP_FILENAME, 'r') as zip_ref:
        zip_ref.extractall(EXTRACTED_DIR)
    print(f"Файлы успешно распакованы в: {EXTRACTED_DIR}")
except Exception as e:
    print(f"Ошибка при распаковке {ZIP_FILENAME}: {e}")
    exit(1)

# Основная папка внутри распакованного архива
MP_FOLDER = os.path.join(EXTRACTED_DIR, "mp")


# Функция для загрузки звука
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


# ЗАГРУЖАЕМ ЗВУКИ С ИСПОЛЬЗОВАНИЕМ РЕАЛЬНЫХ ИМЕН ИЗ ВЫВОДА
print("\nЗагрузка звуков с реальными именами файлов...")

# Музыка
MUSIC_MENU = load_sound_from_mp('OST/îÑ¡ε/ä½∩îÑ¡ε.mp3')  # OST/Меню/ДляМеню.mp3
MUSIC_ATTACKS1 = load_sound_from_mp('OST/ÇΓá¬á/ÇΓá¬á1.mp3')  # OST/Атака/Атака1.mp3
MUSIC_ATTACKS2 = load_sound_from_mp('OST/ÇΓá¬á/ÇΓá¬á2.mp3')  # OST/Атака/Атака2.mp3
MUSIC_ATTACKS3 = load_sound_from_mp('OST/ÇΓá¬á/ÇΓá¬á3.mp3')  # OST/Атака/Атака3.mp3
MUSIC_UNITED1 = load_sound_from_mp('OST/Äíδτ¡á∩/Äíδτ¡á∩1.mp3')  # OST/Обычная/Обычная1.mp3
MUSIC_UNITED2 = load_sound_from_mp('OST/Äíδτ¡á∩/Äíδτ¡á∩2.mp3')  # OST/Обычная/Обычная2.mp3
MUSIC_UNITED3 = load_sound_from_mp('OST/Äíδτ¡á∩/Äíδτ¡á∩3.mp3')  # OST/Обычная/Обычная3.mp3

# Звуки попаданий
HIT = [
    load_sound_from_mp('æΓαÑ½∞íá/Å«»«ñá¡¿Ñ/»1.mp3'),  # Стрельба/Попадание/п1.mp3
    load_sound_from_mp('æΓαÑ½∞íá/Å«»«ñá¡¿Ñ/»2.mp3'),  # Стрельба/Попадание/п2.mp3
    load_sound_from_mp('æΓαÑ½∞íá/Å«»«ñá¡¿Ñ/»3.mp3'),  # Стрельба/Попадание/п3.mp3
    load_sound_from_mp('æΓαÑ½∞íá/Å«»«ñá¡¿Ñ/»4.mp3'),  # Стрельба/Попадание/п4.mp3
    load_sound_from_mp('æΓαÑ½∞íá/Å«»«ñá¡¿Ñ/»5.mp3'),  # Стрельба/Попадание/п5.mp3
    load_sound_from_mp('æΓαÑ½∞íá/Å«»«ñá¡¿Ñ/»6.mp3'),  # Стрельба/Попадание/п6.mp3
    load_sound_from_mp('æΓαÑ½∞íá/Å«»«ñá¡¿Ñ/»7.mp3')  # Стрельба/Попадание/п7.mp3
]

# Звуки медной турели
SOUND_COPPER_TURRET = [
    load_sound_from_mp('æΓαÑ½∞íá/ÆπαÑ½∞/îÑñ¡á∩/Γ1.mp3'),  # Стрельба/Турель/Медная/т1.mp3
    load_sound_from_mp('æΓαÑ½∞íá/ÆπαÑ½∞/îÑñ¡á∩/Γ2.mp3'),  # Стрельба/Турель/Медная/т2.mp3
    load_sound_from_mp('æΓαÑ½∞íá/ÆπαÑ½∞/îÑñ¡á∩/Γ3.mp3')  # Стрельба/Турель/Медная/т3.mp3
]

# Звуки бронзовой турели
SOUND_BRONZE_TURRET = [
    load_sound_from_mp('æΓαÑ½∞íá/ÆπαÑ½∞/üα«¡ºáóá∩/Γ1.mp3'),  # Стрельба/Турель/Бронзовая/т1.mp3
    load_sound_from_mp('æΓαÑ½∞íá/ÆπαÑ½∞/üα«¡ºáóá∩/Γ2.mp3')  # Стрельба/Турель/Бронзовая/т2.mp3
]

# Звуки длинноствольной турели
SOUND_LONG_BARRELED_TURRET = [
    load_sound_from_mp('æΓαÑ½∞íá/ÆπαÑ½∞/ä½¿¡¡«ßΓó«½∞¡á∩/Γ1.mp3'),  # Стрельба/Турель/Длинноствольная/т1.mp3
    load_sound_from_mp('æΓαÑ½∞íá/ÆπαÑ½∞/ä½¿¡¡«ßΓó«½∞¡á∩/Γ2.mp3'),  # Стрельба/Турель/Длинноствольная/т2.mp3
    load_sound_from_mp('æΓαÑ½∞íá/ÆπαÑ½∞/ä½¿¡¡«ßΓó«½∞¡á∩/Γ3.mp3')  # Стрельба/Турель/Длинноствольная/т3.mp3
]

print("\nЗагрузка звуков завершена!")

# Автоматическая очистка при выходе
import atexit

atexit.register(cleanup_directory)
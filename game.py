# game.py
import arcade
from arcade.camera import Camera2D

from arcade.gui import UIManager
from typing import Dict, List, Optional, Any, Tuple, Union
import json
import math
import random
from constants import TILE_SIZE, SPRITE_SCALE, WAVES, BUILDING_HP, BUILDING_KEYS
from core import Core, ResourceCost
from player import Player
from buildings import (Building, DroneStation, CoalDrill, ElectricDrill,
                       BronzeFurnace, SiliconFurnace, CircuitFactory, AmmoFactory,
                       CopperTurret, BronzeTurret, LongRangeTurret, Drone)
from enemies import (Bug, Beetle, ArmoredBeetle, SpittingBeetle,
                     DominicTorettoBeetle, HarkerBeetle)


class MyGame(arcade.Window):
    """Основной класс игры - управляет всем игровым процессом"""

    def __init__(self, width: int, height: int, title: str, map_filename: str):
        """
        Инициализация игры

        Параметры:
        width: int - ширина окна в пикселях
        height: int - высота окна в пикселях
        title: str - заголовок окна
        map_filename: str - путь к файлу карты JSON

        Атрибуты инициализации:
        self.width/height: int - размеры окна
        self.title: str - заголовок
        self.map_filename: str - имя файла карты

        Атрибуты камер:
        self.world_camera: Camera2D - камера для игрового мира (следует за игроком)
        self.gui_camera: Camera2D - камера для UI (фиксированная, не двигается)

        Игровые сущности:
        self.player: Player - космический корабль игрока
        self.core: Core - ядро, которое нужно защитить
        self.buildings: arcade.SpriteList - все здания в игре
        self.bullets: arcade.SpriteList - все пули (турелей и жуков)
        self.bugs: arcade.SpriteList - все враги
        self.drones: arcade.SpriteList - все дроны
        self.grid: List[List[Optional[Building]]] - сетка карты для проверки коллизий

        Параметры карты:
        self.map_width: int - ширина карты в клетках
        self.map_height: int - высота карты в клетках
        self.map_width_pixels: int - ширина карты в пикселях
        self.map_height_pixels: int - высота карты в пикселях

        Система волн:
        self.waves: List[Tuple[float, List[str]]] - расписание волн [(время_до_волны, [типы_жуков])]
        self.current_wave_index: int - индекс текущей волны
        self.wave_timer: float - таймер до следующей волны в секундах
        self.spawn_point: Tuple[float, float] - точка спавна жуков (координаты в пикселях)
        self.last_bug_spawn_time: float - время последнего спавна жука для плавного появления

        Система строительства:
        self.selected_building_type: Optional[str] = None - выбранный тип здания для постройки
        self.delete_mode: bool = False - режим сноса зданий
        self.programming_station: Optional[DroneStation] = None - станция в режиме программирования
        self.programming_step: int = 0 - шаг программирования (0-неактивно, 1-выбран источник, 2-выбран приемник)
        self.programming_source: Optional[Building] = None - источник для программирования
        self.programming_destination: Optional[Building] = None - приемник для программирования

        Состояние игры:
        self.game_state: str = "playing" - текущее состояние ('playing', 'game_over', 'victory')
        self.hovered_building: Optional[Building] = None - здание под курсором для отображения информации
        self.pressed_keys: set = set() - множество нажатых клавиш для обработки движения

        UI система:
        self.ui_manager: UIManager - менеджер пользовательского интерфейса
        self.info_text: str = "" - текст информации для отображения
        self.info_position: Tuple[float, float] = (0, 0) - позиция текста информации
        """
        super().__init__(width, height, title)
        self.map_filename = map_filename

        # Инициализация камер
        self.world_camera = Camera2D()
        self.gui_camera = Camera2D()
        self.world_camera.viewport = (0, 0, width, height)
        self.gui_camera.viewport = (0, 0, width, height)

        # Инициализация игровых сущностей
        self.player = None
        self.core = None
        self.buildings = arcade.SpriteList()
        self.bullets = arcade.SpriteList()
        self.bugs = arcade.SpriteList()
        self.drones = arcade.SpriteList()
        self.grid = None
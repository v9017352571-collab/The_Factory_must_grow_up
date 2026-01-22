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
        self.current_user_id = None
        self.current_user = None
        self.current_level = 1

        # Статистика игры
        self.game_stats = GameStats()

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

        def calculate_level_stats(self) -> Dict[str, Any]:
            """Вычисление статистики для текущего уровня"""
            return {
                'level_number': self.current_level,
                'score': self.calculate_score(),
                'enemies_killed': self.enemies_killed,
                'time_spent': self.game_time,
                'waves_completed': self.current_wave_index,
                'resources_collected': self.calculate_resources_collected(),
                'buildings_built': len(self.buildings),
                'drones_used': len(self.drones)
            }

        def on_victory(self):
            """Вызывается при победе на уровне"""
            level_stats = self.calculate_level_stats()

            # Сохраняем в общую статистику
            self.game_stats.add_level_result(level_stats)

            # Показываем соответствующее окно
            from menu import show_level_complete, show_final_results

            total_levels = 5  # Всего уровней в игре

            if self.current_level < total_levels:
                # Показываем окно завершения уровня
                show_level_complete(
                    level_data=level_stats,
                    user_id=self.current_user_id,
                    username=self.current_user
                )
            else:
                # Показываем финальное окно
                total_stats = self.game_stats.get_total_stats()
                show_final_results(
                    total_stats=total_stats,
                    user_id=self.current_user_id,
                    username=self.current_user
                )

        def on_defeat(self, reason: str = "Ядро разрушено"):
            """Вызывается при поражении"""
            from menu import show_game_over

            stats = {
                'score': self.calculate_score(),
                'enemies_killed': self.enemies_killed,
                'time_survived': self.game_time,
                'waves_completed': self.current_wave_index
            }

            show_game_over(
                level_number=self.current_level,
                reason=reason,
                stats=stats,
                user_id=self.current_user_id
            )


class GameStats:
    """Класс для хранения и обработки статистики игры"""

    def __init__(self):
        self.level_results = []
        self.total_score = 0
        self.total_enemies_killed = 0
        self.total_play_time = 0.0
        self.levels_completed = 0

    def add_level_result(self, level_stats: Dict[str, Any]):
        """Добавляет результат уровня"""
        self.level_results.append(level_stats)
        self.total_score += level_stats.get('score', 0)
        self.total_enemies_killed += level_stats.get('enemies_killed', 0)
        self.total_play_time += level_stats.get('time_spent', 0)
        self.levels_completed += 1

    def get_total_stats(self) -> Dict[str, Any]:
        """Возвращает общую статистику"""
        return {
            'total_score': self.total_score,
            'total_enemies_killed': self.total_enemies_killed,
            'total_play_time': self.total_play_time,
            'levels_completed': self.levels_completed,
            'level_results': self.level_results
        }
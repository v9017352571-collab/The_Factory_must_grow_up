import sqlite3
import json
from datetime import datetime
from typing import List, Tuple, Dict, Any, Optional


class GameDatabase:
    """База данных для хранения пользователей и рекордов"""

    def __init__(self, db_name: str = "game_database.db"):
        """
        Инициализация базы данных

        Структура таблиц:
        1. users - информация о пользователях
        2. level_records - рекорды по уровням
        3. global_records - глобальные рекорды
        4. player_progress - прогресс игроков
        """
        self.db_name = db_name
        self.connection = sqlite3.connect(db_name)
        self.cursor = self.connection.cursor()
        self.create_tables()

    def create_tables(self):
        """Создание таблиц базы данных"""

        # Таблица пользователей
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                total_play_time INTEGER DEFAULT 0,
                total_games_played INTEGER DEFAULT 0,
                total_enemies_killed INTEGER DEFAULT 0,
                favorite_turret TEXT DEFAULT 'Медная турель'
            )
        ''')

        # Таблица рекордов по уровням
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS level_records (
                record_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                level_number INTEGER NOT NULL,
                score INTEGER NOT NULL,
                enemies_killed INTEGER NOT NULL,
                time_spent REAL NOT NULL,
                waves_completed INTEGER NOT NULL,
                resources_collected INTEGER NOT NULL,
                buildings_built INTEGER NOT NULL,
                drones_used INTEGER NOT NULL,
                date_achieved TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                difficulty TEXT DEFAULT 'normal',
                FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
                UNIQUE(user_id, level_number, difficulty)
            )
        ''')

        # Таблица глобальных рекордов
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS global_records (
                record_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                total_score INTEGER NOT NULL,
                levels_completed INTEGER NOT NULL,
                total_enemies_killed INTEGER NOT NULL,
                total_play_time REAL NOT NULL,
                date_achieved TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
            )
        ''')

        # Таблица прогресса игроков
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS player_progress (
                progress_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER UNIQUE,
                current_level INTEGER DEFAULT 1,
                unlocked_levels INTEGER DEFAULT 1,
                last_played TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                saved_game_state TEXT,  -- JSON с состоянием игры
                preferences TEXT,  -- JSON с настройками игрока
                FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
            )
        ''')

        self.connection.commit()

    def register_user(self, username: str) -> int:
        """
        Регистрация нового пользователя

        Возвращает:
        int - ID нового пользователя или -1 при ошибке
        """
        try:
            self.cursor.execute(
                "INSERT INTO users (username) VALUES (?)",
                (username,)
            )
            user_id = self.cursor.lastrowid

            # Создаем запись прогресса для нового пользователя
            self.cursor.execute(
                "INSERT INTO player_progress (user_id) VALUES (?)",
                (user_id,)
            )

            self.connection.commit()
            return user_id
        except sqlite3.IntegrityError:
            # Пользователь уже существует
            return self.get_user_id(username)

    def get_user_id(self, username: str) -> int:
        """Получение ID пользователя по имени"""
        self.cursor.execute(
            "SELECT user_id FROM users WHERE username = ?",
            (username,)
        )
        result = self.cursor.fetchone()
        return result[0] if result else -1

    def save_level_record(self, user_id: int, level_data: Dict[str, Any]):
        """
        Сохранение рекорда уровня

        Параметры:
        user_id: int - ID пользователя
        level_data: Dict - данные уровня:
            - level_number: int (1-3)
            - score: int
            - enemies_killed: int
            - time_spent: float
            - waves_completed: int
            - resources_collected: int
            - buildings_built: int
            - drones_used: int
            - difficulty: str
        """
        try:
            # Проверяем, что уровень в диапазоне 1-3
            level_number = level_data['level_number']
            if not 1 <= level_number <= 3:
                print(f"Ошибка: уровень {level_number} вне диапазона 1-3")
                return

            self.cursor.execute('''
                INSERT OR REPLACE INTO level_records 
                (user_id, level_number, score, enemies_killed, time_spent, 
                 waves_completed, resources_collected, buildings_built, drones_used, difficulty)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                user_id,
                level_number,
                level_data['score'],
                level_data['enemies_killed'],
                level_data['time_spent'],
                level_data['waves_completed'],
                level_data['resources_collected'],
                level_data['buildings_built'],
                level_data['drones_used'],
                level_data.get('difficulty', 'normal')
            ))

            # Обновляем общую статистику пользователя
            self.cursor.execute('''
                UPDATE users 
                SET total_games_played = total_games_played + 1,
                    total_enemies_killed = total_enemies_killed + ?,
                    total_play_time = total_play_time + ?
                WHERE user_id = ?
            ''', (
                level_data['enemies_killed'],
                level_data['time_spent'],
                user_id
            ))

            self.connection.commit()
        except Exception as e:
            print(f"Ошибка сохранения рекорда: {e}")

    def save_global_record(self, user_id: int, total_stats: Dict[str, Any]):
        """
        Сохранение глобального рекорда

        Параметры:
        user_id: int - ID пользователя
        total_stats: Dict - общая статистика:
            - total_score: int
            - levels_completed: int
            - total_enemies_killed: int
            - total_play_time: float
        """
        try:
            self.cursor.execute('''
                INSERT INTO global_records 
                (user_id, total_score, levels_completed, total_enemies_killed, total_play_time)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                user_id,
                total_stats['total_score'],
                total_stats['levels_completed'],
                total_stats['total_enemies_killed'],
                total_stats['total_play_time']
            ))
            self.connection.commit()
        except Exception as e:
            print(f"Ошибка сохранения глобального рекорда: {e}")

    def get_top_level_records(self, level_number: int, limit: int = 10) -> List[Tuple]:
        """
        Получение топ рекордов для конкретного уровня

        Возвращает:
        List[Tuple] - список кортежей (username, score, time_spent, date_achieved)
        """
        self.cursor.execute('''
            SELECT u.username, lr.score, lr.time_spent, lr.date_achieved
            FROM level_records lr
            JOIN users u ON lr.user_id = u.user_id
            WHERE lr.level_number = ?
            ORDER BY lr.score DESC, lr.time_spent ASC
            LIMIT ?
        ''', (level_number, limit))

        return self.cursor.fetchall()

    def get_top_global_records(self, limit: int = 10) -> List[Tuple]:
        """
        Получение топ глобальных рекордов

        Возвращает:
        List[Tuple] - список кортежей (username, total_score, levels_completed, date_achieved)
        """
        self.cursor.execute('''
            SELECT u.username, gr.total_score, gr.levels_completed, gr.date_achieved
            FROM global_records gr
            JOIN users u ON gr.user_id = u.user_id
            ORDER BY gr.total_score DESC, gr.date_achieved ASC
            LIMIT ?
        ''', (limit,))

        return self.cursor.fetchall()

    def get_user_stats(self, user_id: int) -> Dict[str, Any]:
        """Получение статистики пользователя"""
        self.cursor.execute('''
            SELECT u.username, u.registration_date, u.total_play_time, 
                   u.total_games_played, u.total_enemies_killed, u.favorite_turret,
                   pp.current_level, pp.unlocked_levels
            FROM users u
            LEFT JOIN player_progress pp ON u.user_id = pp.user_id
            WHERE u.user_id = ?
        ''', (user_id,))

        result = self.cursor.fetchone()
        if result:
            return {
                'username': result[0],
                'registration_date': result[1],
                'total_play_time': result[2],
                'total_games_played': result[3],
                'total_enemies_killed': result[4],
                'favorite_turret': result[5],
                'current_level': result[6] or 1,
                'unlocked_levels': result[7] or 1
            }
        return {}

    def get_user_level_records(self, user_id: int) -> Dict[int, Dict]:
        """Получение всех рекордов пользователя по уровням"""
        self.cursor.execute('''
            SELECT level_number, score, enemies_killed, time_spent, 
                   waves_completed, date_achieved
            FROM level_records
            WHERE user_id = ?
            ORDER BY level_number
        ''', (user_id,))

        records = {}
        for row in self.cursor.fetchall():
            records[row[0]] = {
                'score': row[1],
                'enemies_killed': row[2],
                'time_spent': row[3],
                'waves_completed': row[4],
                'date_achieved': row[5]
            }

        return records

    def update_player_progress(self, user_id: int, current_level: int, unlocked_levels: int = None):
        """
        Обновление прогресса игрока

        Параметры:
        user_id: int - ID пользователя
        current_level: int - текущий уровень
        unlocked_levels: int - открытые уровни (если None, то max(current_level, unlocked_levels))
        """
        if unlocked_levels is None:
            # Получаем текущий прогресс
            self.cursor.execute(
                "SELECT unlocked_levels FROM player_progress WHERE user_id = ?",
                (user_id,)
            )
            current = self.cursor.fetchone()
            current_unlocked = current[0] if current else 1

            unlocked_levels = max(current_unlocked, current_level)

        try:
            self.cursor.execute('''
                UPDATE player_progress 
                SET current_level = ?, 
                    unlocked_levels = ?,
                    last_played = CURRENT_TIMESTAMP
                WHERE user_id = ?
            ''', (current_level, unlocked_levels, user_id))

            self.connection.commit()
        except Exception as e:
            print(f"Ошибка обновления прогресса: {e}")

    def save_game_state(self, user_id: int, game_state: Dict[str, Any]):
        """
        Сохранение состояния игры для продолжения

        Параметры:
        user_id: int - ID пользователя
        game_state: Dict - состояние игры в формате JSON
        """
        try:
            self.cursor.execute('''
                UPDATE player_progress 
                SET saved_game_state = ?
                WHERE user_id = ?
            ''', (json.dumps(game_state), user_id))

            self.connection.commit()
        except Exception as e:
            print(f"Ошибка сохранения состояния: {e}")

    def load_game_state(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Загрузка сохраненного состояния игры"""
        self.cursor.execute(
            "SELECT saved_game_state FROM player_progress WHERE user_id = ?",
            (user_id,)
        )

        result = self.cursor.fetchone()
        if result and result[0]:
            return json.loads(result[0])
        return None

    def close(self):
        """Закрытие соединения с БД"""
        self.connection.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


# Создание индексов для оптимизации запросов
def create_indexes(db: GameDatabase):
    """Создание индексов для ускорения запросов"""
    indexes = [
        "CREATE INDEX IF NOT EXISTS idx_level_records_level ON level_records(level_number)",
        "CREATE INDEX IF NOT EXISTS idx_level_records_score ON level_records(score DESC)",
        "CREATE INDEX IF NOT EXISTS idx_global_records_score ON global_records(total_score DESC)",
        "CREATE INDEX IF NOT EXISTS idx_users_username ON users(username)",
        "CREATE INDEX IF NOT EXISTS idx_progress_user ON player_progress(user_id)"
    ]

    for index_sql in indexes:
        db.cursor.execute(index_sql)

    db.connection.commit()


# Инициализация базы данных при импорте
def init_database():
    """Инициализация базы данных при запуске игры"""
    db = GameDatabase()
    create_indexes(db)
    db.close()
    print("База данных инициализирована")


if __name__ == "__main__":
    # Тестирование базы данных
    db = GameDatabase()

    # Создаем тестового пользователя
    user_id = db.register_user("TestPlayer")
    print(f"Создан пользователь с ID: {user_id}")

    # Сохраняем тестовый рекорд
    test_record = {
        'level_number': 1,
        'score': 1500,
        'enemies_killed': 25,
        'time_spent': 180.5,
        'waves_completed': 5,
        'resources_collected': 100,
        'buildings_built': 15,
        'drones_used': 3,
        'difficulty': 'normal'
    }

    db.save_level_record(user_id, test_record)
    print("Тестовый рекорд сохранен")

    # Получаем статистику
    stats = db.get_user_stats(user_id)
    print(f"Статистика пользователя: {stats}")

    db.close()
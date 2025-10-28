import sqlite3
from pathlib import Path
import bcrypt

DB_PATH = Path("data/users.db")

def init_db():
    """Создает файл БД и таблицы, если они отсутствуют."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Таблица пользователей
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        );
    """)

    # Таблица результатов
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            test_name TEXT NOT NULL,
            score INTEGER NOT NULL,
            date TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id)
        );
    """)

    conn.commit()

    # Проверка наличия пользователя teacher
    cursor.execute("SELECT id FROM users WHERE username = 'teacher'")
    if not cursor.fetchone():
        #hashed = bcrypt.hashpw("teacher".encode(), bcrypt.gensalt())
        cursor.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", ("teacher", "teacher"))
        conn.commit()

    conn.close()


def get_connection():
    """Возвращает соединение с БД."""
    return sqlite3.connect(DB_PATH)

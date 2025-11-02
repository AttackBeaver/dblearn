import sqlite3
import bcrypt
import os

DB_PATH = "data/users.db"


def init_db():
    os.makedirs("data", exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        username TEXT PRIMARY KEY,
        password TEXT NOT NULL,
        role TEXT NOT NULL
    )''')
    conn.commit()
    conn.close()

    # Создание преподавателя, если его нет
    # create_default_teacher()


# def create_default_teacher():
#     conn = sqlite3.connect(DB_PATH)
#     c = conn.cursor()
#     c.execute("SELECT username FROM users WHERE username = ?", ("teacher",))
#     if not c.fetchone():
#         plain_password = ""
#         hashed = bcrypt.hashpw(
#             plain_password.encode('utf-8'), bcrypt.gensalt())
#         c.execute("INSERT INTO users VALUES (?, ?, ?)",
#                   ("teacher", hashed, "Преподаватель"))
#         conn.commit()
#     conn.close()


def add_user(username, password, role):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    c.execute("INSERT OR REPLACE INTO users VALUES (?, ?, ?)",
              (username, hashed, role))
    conn.commit()
    conn.close()


def authenticate_user(username, password):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT password FROM users WHERE username = ?", (username,))
    data = c.fetchone()
    conn.close()
    if data:
        return bcrypt.checkpw(password.encode('utf-8'), data[0])
    return False


def get_user_role(username):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT role FROM users WHERE username = ?", (username,))
    data = c.fetchone()
    conn.close()
    return data[0] if data else None


def get_all_students():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT username FROM users WHERE role = 'Студент'")
    students = [row[0] for row in c.fetchall()]
    conn.close()
    return students

import streamlit as st
import bcrypt
from datetime import datetime
from modules.db_init import get_connection

# -------------------------------
# Функции работы с пользователями
# -------------------------------

def user_exists(username: str) -> bool:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
    exists = cursor.fetchone() is not None
    conn.close()
    return exists


def register_user(username: str, password: str) -> bool:
    """Создает нового пользователя, возвращает True при успехе."""
    if user_exists(username):
        return False
    conn = get_connection()
    cursor = conn.cursor()
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    cursor.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", (username, hashed))
    conn.commit()
    conn.close()
    return True


def validate_user(username: str, password: str) -> bool:
    """Проверяет корректность логина и пароля."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT password_hash FROM users WHERE username = ?", (username,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        return False
    return bcrypt.checkpw(password.encode(), row[0])


# -------------------------------
# Работа с сессией Streamlit
# -------------------------------

def login_form():
    """Форма входа и регистрации в Streamlit."""
    st.subheader("Авторизация")
    tab_login, tab_register = st.tabs(["Войти", "Регистрация"])

    with tab_login:
        username = st.text_input("Имя пользователя", key="login_user")
        password = st.text_input("Пароль", type="password", key="login_pass")
        if st.button("Войти"):
            if validate_user(username, password):
                st.session_state["user"] = username
                st.session_state["login_time"] = datetime.now().isoformat()
                st.success(f"Добро пожаловать, {username}")
            else:
                st.error("Неверное имя пользователя или пароль")

    with tab_register:
        new_user = st.text_input("Имя нового пользователя", key="reg_user")
        new_pass = st.text_input("Пароль", type="password", key="reg_pass")
        if st.button("Зарегистрироваться"):
            if register_user(new_user, new_pass):
                st.success("Пользователь успешно зарегистрирован")
            else:
                st.warning("Имя пользователя уже занято")


def logout_button():
    """Кнопка выхода из системы."""
    if "user" in st.session_state:
        if st.button("Выйти"):
            del st.session_state["user"]
            st.info("Вы вышли из системы.")

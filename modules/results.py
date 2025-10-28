import streamlit as st
from datetime import datetime
from modules.db_init import get_connection

# -------------------------------
# Сохранение результатов
# -------------------------------

def save_result(username: str, test_name: str, score: int, total: int):
    """Сохраняет результат прохождения теста пользователем."""
    conn = get_connection()
    cursor = conn.cursor()

    # Получаем id пользователя
    cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return False

    user_id = row[0]
    date_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute("""
        INSERT INTO results (user_id, test_name, score, date)
        VALUES (?, ?, ?, ?)
    """, (user_id, test_name, score, date_str))

    conn.commit()
    conn.close()
    return True


# -------------------------------
# Отображение истории результатов
# -------------------------------

def show_user_results(username: str):
    """Выводит историю результатов пользователя в Streamlit."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT test_name, score, date
        FROM results
        JOIN users ON results.user_id = users.id
        WHERE users.username = ?
        ORDER BY date DESC
    """, (username,))
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        st.info("Вы ещё не проходили тесты.")
        return

    st.subheader("📊 История ваших результатов")
    for test_name, score, date in rows:
        st.write(f"**{test_name}** — {score} баллов ({date})")

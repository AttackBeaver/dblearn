import streamlit as st
from modules.test_loader import load_test, validate_test_structure


def run_quiz(test_name: str):
    """
    Основная функция проведения теста.
    Возвращает итоговый результат (количество правильных ответов).
    """
    try:
        test_data = load_test(test_name)
    except FileNotFoundError:
        st.error("Выбранный тест не найден.")
        return None

    if not validate_test_structure(test_data):
        st.error("Ошибка в структуре теста.")
        return None

    st.header(f"Тема: {test_data['topic']}")
    score = 0

    for i, q in enumerate(test_data["questions"], start=1):
        st.markdown(f"**Вопрос {i}: {q['question']}**")
        choice = st.radio(
            "Выберите ответ:",
            q["options"],
            key=f"q_{i}"
        )

        # Проверка ответа
        correct_index = q["answer"]
        if st.session_state.get(f"answered_{i}") is None:
            if st.button(f"Проверить {i}", key=f"check_{i}"):
                st.session_state[f"answered_{i}"] = (choice == q["options"][correct_index])

        if st.session_state.get(f"answered_{i}") is not None:
            if st.session_state[f"answered_{i}"]:
                st.success("✅ Правильно")
                score += 1
            else:
                st.error(f"❌ Неверно. Правильный ответ: {q['options'][correct_index]}")

        st.divider()

    total_questions = len(test_data["questions"])
    st.subheader(f"Результат: {score} из {total_questions}")
    return {"score": score, "total": total_questions}

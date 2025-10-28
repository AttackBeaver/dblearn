import streamlit as st
import json
from pathlib import Path

TESTS_PATH = Path("data/tests")
RESULTS_PATH = Path("data/results")


def teacher_panel():
    """Панель преподавателя для управления тестами и просмотра результатов."""
    st.title("🎛 Панель преподавателя")

    TESTS_PATH.mkdir(parents=True, exist_ok=True)
    RESULTS_PATH.mkdir(parents=True, exist_ok=True)

    mode = st.radio(
        "Выберите действие:",
        ["Создать новый тест", "Редактировать существующий", "Просмотреть результаты"],
    )

    # === СОЗДАНИЕ НОВОГО ТЕСТА ===
    if mode == "Создать новый тест":
        test_name = st.text_input("Введите имя теста (латиницей, без пробелов)")
        topic = st.text_input("Тема теста")
        questions = []

        num_q = st.number_input("Количество вопросов", min_value=1, max_value=50, value=3)
        for i in range(int(num_q)):
            st.markdown(f"**Вопрос {i+1}**")
            question = st.text_input(f"Текст вопроса {i+1}")
            options = []
            for j in range(4):
                options.append(st.text_input(f"Вариант {j+1} для вопроса {i+1}"))
            correct = st.number_input(
                f"Номер правильного ответа (0-3)", min_value=0, max_value=3, value=0, key=f"ans{i}"
            )
            questions.append({"question": question, "options": options, "answer": correct})

        if st.button("💾 Сохранить тест"):
            if not test_name:
                st.warning("Введите имя теста.")
            else:
                test_data = {"topic": topic, "questions": questions}
                file_path = TESTS_PATH / f"{test_name}.json"
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(test_data, f, ensure_ascii=False, indent=2)
                st.success(f"Тест '{test_name}' успешно сохранён!")

    # === РЕДАКТИРОВАНИЕ ТЕСТА ===
    elif mode == "Редактировать существующий":
        tests = [f.stem for f in TESTS_PATH.glob("*.json")]
        if not tests:
            st.info("Нет доступных тестов для редактирования.")
            return
        test_choice = st.selectbox("Выберите тест:", tests)
        file_path = TESTS_PATH / f"{test_choice}.json"

        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        st.subheader(f"Редактирование теста: {data['topic']}")
        new_topic = st.text_input("Изменить тему", value=data["topic"])

        for i, q in enumerate(data["questions"], start=1):
            st.markdown(f"**Вопрос {i}**")
            q["question"] = st.text_input(f"Вопрос {i}", value=q["question"])
            for j, opt in enumerate(q["options"]):
                q["options"][j] = st.text_input(f"Вариант {j+1} для {i}", value=opt)
            q["answer"] = st.number_input(
                f"Правильный вариант (0-3)", min_value=0, max_value=3, value=q["answer"], key=f"edit_{i}"
            )

        if st.button("💾 Сохранить изменения"):
            data["topic"] = new_topic
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            st.success("Изменения сохранены!")

    # === ПРОСМОТР РЕЗУЛЬТАТОВ ===
    elif mode == "Просмотреть результаты":
        st.subheader("📊 Результаты студентов")
        result_files = sorted(RESULTS_PATH.glob("*.json"))

        if not result_files:
            st.info("Пока нет сохранённых результатов.")
            return

        for file in result_files:
            username = file.stem.replace("_results", "")
            with open(file, "r", encoding="utf-8") as f:
                results = json.load(f)

            st.markdown(f"### 👤 {username}")
            for test_name, score in results.items():
                st.write(f"**{test_name}** — {score['correct']}/{score['total']} правильных ответов")
            st.divider()

import streamlit as st
from modules.db_init import init_db
from modules import auth, test_loader, quiz_engine, results, teacher_panel

st.set_page_config(page_title="DBLearn", page_icon="🧩")
init_db()

if "user" not in st.session_state:
    auth.login_form()
    st.stop()

# Навигация
st.sidebar.title("Навигация")
menu_items = ["Тесты", "Результаты", "Выход"]
if st.session_state["user"] == "teacher":
    menu_items.insert(1, "Панель преподавателя")

menu = st.sidebar.radio("Раздел", menu_items)

if menu == "Тесты":
    st.title("🎓 Обучение и тестирование по SQL")
    tests = test_loader.get_available_tests()
    if not tests:
        st.warning("Тесты пока не добавлены.")
    else:
        test_choice = st.selectbox("Выберите тест:", tests)
        if st.button("Начать тест"):
            result = quiz_engine.run_quiz(test_choice)
            if result and st.button("💾 Сохранить результат"):
                results.save_result(
                    username=st.session_state["user"],
                    test_name=test_choice,
                    score=result["score"],
                    total=result["total"]
                )
                st.success("Результат сохранён.")

elif menu == "Панель преподавателя":
    teacher_panel.teacher_panel()

elif menu == "Результаты":
    st.title("📈 Ваши результаты")
    results.show_user_results(st.session_state["user"])

elif menu == "Выход":
    auth.logout_button()

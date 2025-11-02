import streamlit as st
import pandas as pd
import time
import plotly
from datetime import datetime, timedelta
from database.db_manager import (
    init_db,
    add_user,
    authenticate_user,
    get_user_role,
    get_all_students,
)

# НАСТРОЙКИ СТРАНИЦЫ
st.set_page_config(
    page_title="DB Learn - Siberian Professional College",
    page_icon="🛢️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Инициализация базы данных
init_db()

# CSS
def inject_custom_css():
    st.markdown("""
    <style>
        /* Основные стили */
         .main-header {
        #     font-size: 2.8rem;
        #     background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        #     -webkit-background-clip: text;
        #     -webkit-text-fill-color: transparent;
             text-align: center;
             margin-bottom: 1rem;
             font-weight: 700;
        # }
        
        .card {
            background: white;
            padding: 1.5rem;
            border-radius: 15px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            border-left: 5px solid #667eea;
            margin: 1rem 0;
            transition: transform 0.3s ease;
        }
        
        .card:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
        }
        
        .teacher-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 2rem;
            border-radius: 15px;
            box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
        }
        
        .student-card {
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            color: white;
            padding: 2rem;
            border-radius: 15px;
            box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
        }
        
        .metric-card {
            background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
            color: white;
            padding: 1.5rem;
            border-radius: 12px;
            text-align: center;
        }
        
        .stButton>button {
            border-radius: 10px;
            font-weight: 600;
            padding: 0.5rem 1rem;
            transition: all 0.3s ease;
        }
        
        .stButton>button:hover {
            transform: translateY(-1px);
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
        }
        
        /* Сайдбар */
        .css-1d391kg {
            background: linear-gradient(180deg, #f8f9fa 0%, #e9ecef 100%);
        }
        
        /* Вкладки */
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
        }
        
        .stTabs [data-baseweb="tab"] {
            height: 50px;
            white-space: pre-wrap;
            border-radius: 10px 10px 0px 0px;
            gap: 8px;
            padding: 10px 16px;
            background-color: #f0f2f6;
        }
        
        .stTabs [aria-selected="true"] {
            background-color: #667eea;
            color: white;
        }
        
        /* Прогресс-бар */
        .stProgress > div > div > div {
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        }
        
        /* Уведомления */
        .notification {
            padding: 1rem;
            border-radius: 10px;
            margin: 0.5rem 0;
            border-left: 4px solid;
        }
        
        .notification-info {
            background-color: #e3f2fd;
            border-left-color: #2196f3;
        }
        
        .notification-warning {
            background-color: #fff3e0;
            border-left-color: #ff9800;
        }
        
        .notification-success {
            background-color: #e8f5e8;
            border-left-color: #4caf50;
        }
    </style>
    """, unsafe_allow_html=True)


# Применяем CSS
inject_custom_css()

# СОСТОЯНИЯ СЕССИИ
if "username" not in st.session_state:
    st.session_state.update({
        "username": None,
        "role": None,
        "mode": "login",
        "page": "home",
        "notifications": [],
        "last_login": None
    })

# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
def show_sidebar():
    """Боковая панель с информацией"""
    with st.sidebar:
        st.markdown("""
            ## 🎓 DB Learn - Siberian Professional College
            ---
             © 2025 *БПОУ ОО «Сибирский профессиональный колледж»*
            Преподаватель/разработчик: **Стариков А.В.** 
            """)

        if st.session_state.username:
            role_emoji = "👨‍🏫" if st.session_state.role == "Преподаватель" else "🎓"
            st.markdown(f"### {role_emoji} {st.session_state.username}")
            st.markdown(f"**Роль:** {st.session_state.role}")

# ФОРМА ВХОДА
def show_login_form():
    col_img, col_form = st.columns([1, 2])

    with col_img:
        st.markdown("""
        <div style='text-align: center; padding: 2rem 0;'>
            <h1 style='font-size: 4rem;'>👋</h1>
            <h2>Добро пожаловать!</h2>
        </div>
        """, unsafe_allow_html=True)

    with col_form:
        st.markdown("### Авторизация")

        with st.form("login_form"):
            username = st.text_input(
                "👤 Логин",
                placeholder="Введите ваш логин",
                help="Введите ваш уникальный идентификатор"
            )
            password = st.text_input(
                "🔒 Пароль",
                type="password",
                placeholder="Введите ваш пароль",
                help="Введите ваш секретный пароль"
            )

            col1, col2, col3 = st.columns([2, 1, 1])
            with col1:
                login_btn = st.form_submit_button(
                    "🚀 Войти в систему",
                    use_container_width=True,
                    type="primary"
                )
            with col2:
                reg_btn = st.form_submit_button(
                    "📝 Регистрация",
                    use_container_width=True
                )
            with col3:
                guest_btn = st.form_submit_button(
                    "👀 Гостевой доступ",
                    use_container_width=True
                )

            if login_btn:
                if username and password:
                    with st.spinner("Проверка учетных данных..."):
                        time.sleep(1)  # Имитация задержки
                        user_ok = authenticate_user(username, password)
                        if user_ok:
                            st.session_state.update({
                                "username": username,
                                "role": get_user_role(username),
                                "last_login": datetime.now().strftime("%d.%m.%Y %H:%M")
                            })
                            st.success("✅ Успешный вход! Перенаправляем...")
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error("❌ Неверный логин или пароль")
                else:
                    st.warning("⚠️ Пожалуйста, заполните все поля")

            if reg_btn:
                st.session_state["mode"] = "register"
                st.rerun()

            if guest_btn:
                st.info("👀 Гостевой доступ пока не доступен")

        st.markdown("---")
        st.markdown("""
        <div style='text-align: center; color: #666;'>
            <small>Нет аккаунта? Зарегистрируйтесь для доступа к материалам</small>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

# ФОРМА РЕГИСТРАЦИИ
def show_register_form():
    st.markdown("### Регистрация нового пользователя")
    st.info("Заполните все поля для создания учетной записи")

    with st.form("register_form"):
        col1, col2 = st.columns(2)

        with col1:
            username = st.text_input(
                "👤 Логин *",
                placeholder="Придумайте уникальный логин",
                help="Минимум 3 символа"
            )
            full_name = st.text_input(
                "👤 Полное имя *",
                placeholder="Иванов Иван Иванович"
            )
            group = st.text_input(
                "👥 Группа *",
                placeholder="Укажите свою группу"
            )

        with col2:
            password = st.text_input(
                "🔒 Пароль *",
                type="password",
                placeholder="Создайте надежный пароль",
                help="Минимум 6 символов"
            )
            confirm_password = st.text_input(
                "🔒 Подтверждение пароля *",
                type="password",
                placeholder="Повторите пароль"
            )

        email = st.text_input(
            "📧 Email",
            placeholder="ivanov@example.com",
            help="Необязательно для заполнения"
        )

        # Индикатор сложности пароля
        if password:
            strength = "🟢 Надежный" if len(password) >= 6 else "🟡 Средний" if len(
                password) >= 4 else "🔴 Слабый"
            st.write(f"**Сложность пароля:** {strength}")

        st.markdown(
            "**По умолчанию все новые пользователи регистрируются как Студенты**")

        col1, col2 = st.columns(2)
        with col1:
            create_btn = st.form_submit_button(
                "✅ Создать аккаунт",
                use_container_width=True,
                type="primary"
            )
        with col2:
            back_btn = st.form_submit_button(
                "↩️ Назад к входу",
                use_container_width=True
            )

        if create_btn:
            if not all([username, password, confirm_password, full_name, group]):
                st.error(
                    "❌ Пожалуйста, заполните все обязательные поля (отмечены *)")
            elif password != confirm_password:
                st.error("❌ Пароли не совпадают")
            elif len(password) < 4:
                st.error("❌ Пароль должен содержать минимум 4 символа")
            else:
                role = "Студент"
                add_user(username, password, role)
                st.success(
                    "🎉 Пользователь успешно зарегистрирован! Теперь войдите в систему.")
                time.sleep(2)
                st.session_state["mode"] = "login"
                st.rerun()

        if back_btn:
            st.session_state["mode"] = "login"
            st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

# ПАНЕЛЬ ПРЕПОДАВАТЕЛЯ
def show_teacher_panel():
    st.markdown(f"### 👨‍🏫 Панель преподавателя")
    st.markdown(
        f"**Добро пожаловать, {st.session_state['username']}!** Рады видеть вас снова.")
    st.markdown('</div>', unsafe_allow_html=True)

    # Статистика в реальном времени
    st.markdown("### 📊 Обзор системы")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        students_count = len(get_all_students())
        st.metric(
            label="👥 Всего студентов",
            value=students_count,
            delta=f"+{students_count % 5} за неделю" if students_count > 0 else None
        )

    with col2:
        st.metric(
            label="🧪 Активных тестов",
            value="0",  # считаем кол-во тестов
            delta=""    # и какие то проценты
        )

    with col3:
        st.metric(
            label="📊 Средний балл",
            value="0",  # считаем средний балл
            delta=""    # и процент повышения/понижения за последние попытки
        )

    with col4:
        st.metric(
            label="⏰ Активность",
            value="0",   # проценты посещения
            delta=""    # и процент повышения/понижения
        )

    # Основные разделы
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📈 Дашборд", "👥 Студенты", "🧩 Тесты", "💻 Практика", "⚙️ Настройки"
    ])

    with tab1:
        show_teacher_dashboard()

    with tab2:
        show_students_management()

    with tab3:
        show_tests_management()

    with tab4:
        show_practice_management()

    with tab5:
        show_teacher_settings()


def show_teacher_dashboard():
    st.markdown("### 📈 Статистика и аналитика")

    # Пример данных для графиков
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### 📅 Активность студентов")
        # добавить инфографику активности

    with col2:
        st.markdown("#### 🎯 Распределение оценок")
        # добавить инфографику оценок


def show_students_management():
    st.markdown("### 👥 Управление студентами")

    # Поиск и фильтры
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        search = st.text_input("🔍 Поиск студента по имени")
    with col2:
        filter_group = st.selectbox(
            "Группа", ["Все"])  # заполнять всеми группами из БД

    students = get_all_students()

    if students:
        st.success(f"🎯 Найдено студентов: {len(students)}")

        # Отображение студентов в карточках
        for i, student in enumerate(students):
            if search.lower() in student.lower() or not search:
                with st.container():
                    st.markdown('<div class="card">', unsafe_allow_html=True)

                    col1, col2, col3, col4 = st.columns([3, 2, 2, 1])

                    with col1:
                        st.write(f"### 🎓 {student}")
                        st.write(
                            f"Группа: {i % 3 + 1} | 📧 {student.lower()}@edu.ru")

                    with col2:
                        st.write("**Успеваемость**")
                        st.write(f"🧪 Тесты: {i % 5}/5")
                        st.write(f"💻 Практика: {i % 3}/3")
                        st.write(f"⭐ Средний балл: {4.0 + (i % 10) * 0.1:.1f}")

                    with col3:
                        if st.button("👁️ Подробнее", key=f"view_{i}"):
                            st.session_state[f"view_student_{i}"] = True

                        if st.session_state.get(f"view_student_{i}"):
                            with st.expander(f"📊 Детальная информация по {student}", expanded=True):
                                show_student_details(student, i)

                    st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.warning("📭 Пока нет зарегистрированных студентов")


def show_student_details(student, index):
    """Детальная информация о студенте"""  # отображать всю информацию о выбранном студенте
    col1, col2 = st.columns(2)

    with col1:
        st.write("**📊 Статистика обучения**")

    with col2:
        st.write("**🎯 Последняя активность**")

    # История оценок
    st.write("**📈 История оценок**")

    if st.button("✏️ Добавить комментарий", key=f"comment_{index}"):
        st.text_area("Комментарий преподавателя", key=f"comment_text_{index}")
        if st.button("💾 Сохранить комментарий", key=f"save_comment_{index}"):
            st.success("Комментарий сохранен!")


def show_tests_management():
    # отображать все тесты и управлять ими
    st.markdown("### 🧩 Управление тестами")

    col1, col2 = st.columns([3, 1])
    with col1:
        st.subheader("📋 Список тестов")
    with col2:
        if st.button("➕ Создать новый тест", use_container_width=True):
            st.session_state["create_test"] = True

    if st.session_state.get("create_test"):
        with st.form("create_test_form"):
            # создавать тесты, сохранять в json
            st.subheader("📝 Создание нового теста")

            test_name = st.text_input("Название теста")
            test_description = st.text_area("Описание теста")

            col1, col2 = st.columns(2)
            with col1:
                questions_count = st.number_input(
                    "Количество вопросов", min_value=1, max_value=50, value=10)
                time_limit = st.number_input(
                    "Лимит времени (минут)", min_value=5, max_value=180, value=60)

            with col2:
                passing_score = st.slider("Проходной балл (%)", 0, 100, 70)
                show_answers = st.checkbox(
                    "Показывать ответы после завершения")

            col1, col2 = st.columns(2)
            with col1:
                if st.form_submit_button("✅ Создать тест", use_container_width=True):
                    st.success(f"Тест '{test_name}' успешно создан!")
                    st.session_state["create_test"] = False
                    st.rerun()
            with col2:
                if st.form_submit_button("❌ Отмена", use_container_width=True):
                    st.session_state["create_test"] = False
                    st.rerun()


def show_practice_management():
    # отображать все практические и управление
    st.markdown("### 💻 Управление практическими работами")

    # надо придумать, как хранить практические

    # Загрузка нового задания - например
    st.markdown("### 📤 Загрузка нового задания")
    with st.form("upload_assignment"):
        assignment_name = st.text_input("Название задания")
        assignment_file = st.file_uploader(
            "Файл с заданием (PDF/DOCX)", type=['pdf', 'docx', 'txt'])
        deadline = st.date_input("Срок сдачи")

        if st.form_submit_button("📤 Опубликовать задание", use_container_width=True):
            if assignment_name and assignment_file:
                st.success(
                    f"Задание '{assignment_name}' успешно опубликовано!")
            else:
                st.error("Заполните все обязательные поля")


def show_teacher_settings():
    # возможно, реализовать управление внешним видом и настройки профиля
    st.markdown("### ⚙️ Настройки преподавателя")

    with st.form("teacher_settings"):
        st.subheader("🎨 Внешний вид")

        col1, col2 = st.columns(2)
        with col1:
            theme = st.selectbox("Тема интерфейса", [
                                 "Светлая", "Темная", "Авто"])
            language = st.selectbox("Язык интерфейса", ["Русский", "English"])

        with col2:
            font_size = st.slider("Размер шрифта", 12, 24, 16)
            compact_mode = st.checkbox("Компактный режим")

        if st.form_submit_button("💾 Сохранить настройки", use_container_width=True):
            st.success("✅ Настройки успешно сохранены!")


# ПАНЕЛЬ СТУДЕНТА
def show_student_panel():
    st.markdown(f"### 🎓 Личный кабинет студента")
    st.markdown(
        f"**Приветствуем, {st.session_state['username']}!** Удачи в обучении!")
    st.markdown('</div>', unsafe_allow_html=True)

    # реализовать панель студента с доступам к открытым тестам, практическим работам, статистикой обучения и настройками профиля

# ВЫХОД ИЗ СИСТЕМЫ
def logout():
    st.session_state.update({
        "username": None,
        "role": None,
        "mode": "login",
        "page": "home"
    })
    st.success("👋 Вы успешно вышли из системы!")
    time.sleep(1)
    st.rerun()


# ГЛАВНАЯ ЛОГИКА ПРИЛОЖЕНИЯ
def main():
    # Показываем боковую панель
    show_sidebar()

    # Основной заголовок (только для неавторизованных пользователей)
    if not st.session_state.username:
        st.markdown(
            '<h1 class="main-header">🛢️ Образовательная платформа: Разработка, администрирование и защита баз данных</h1>', unsafe_allow_html=True)
        st.markdown("---")

    # Логика отображения контента
    if st.session_state.username:
        # Кнопка выхода в верхнем правом углу
        col1, col2 = st.columns([5, 1])
        with col2:
            if st.button("➜] Выход", use_container_width=True):
                logout()

        # Отображение соответствующей панели
        if st.session_state.role == "Преподаватель":
            show_teacher_panel()
        else:
            show_student_panel()
    else:
        # Формы входа/регистрации
        if st.session_state["mode"] == "login":
            show_login_form()
        else:
            show_register_form()


if __name__ == "__main__":
    main()

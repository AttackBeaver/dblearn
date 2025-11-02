import streamlit as st
import pandas as pd
import time
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
from data.db_manager import (
    init_db,
    add_user,
    authenticate_user,
    get_user_role,
    get_all_students,
    get_student_data,
    create_test,
    get_teacher_tests,
    get_test_questions,
    get_available_tests,
    submit_test_answers,
    create_secure_question,
    get_test_results,
    get_test_by_id,
    get_group_statistics,
    get_student_progress,
    get_test_analytics,
    get_student_ranking,
    get_teacher_dashboard_stats
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

# CSS с поддержкой темной темы
def inject_custom_css():
    st.markdown("""
    <style>
        /* Универсальные стили для обеих тем */
        .main-header {
            text-align: center;
            margin-bottom: 1rem;
            font-weight: 700;
        }
        
        /* Упрощенные карточки - убираем сложные градиенты */
        .card {
            padding: 1.5rem;
            border-radius: 10px;
            margin: 1rem 0;
            border: 1px solid #e0e0e0;
            background-color: inherit;
        }
        
        .stButton>button {
            border-radius: 8px;
            font-weight: 600;
            padding: 0.5rem 1rem;
        }
        
        /* Упрощенные вкладки */
        .stTabs [data-baseweb="tab-list"] {
            gap: 4px;
        }
        
        .stTabs [data-baseweb="tab"] {
            height: 40px;
            border-radius: 8px 8px 0px 0px;
            padding: 8px 12px;
        }
        
        .stTabs [aria-selected="true"] {
            background-color: #667eea;
            color: white;
        }
        
        /* Прогресс-бар */
        .stProgress > div > div > div {
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        }
        
        /* Базовые уведомления */
        .notification {
            padding: 1rem;
            border-radius: 8px;
            margin: 0.5rem 0;
            border-left: 4px solid;
        }
        
        /* Убираем сложные CSS переменные и медиа-запросы */
        .form-section {
            padding: 1rem;
            border-radius: 8px;
            margin: 1rem 0;
            border: 1px solid #e0e0e0;
        }
        
        .question-item {
            padding: 1rem;
            border-radius: 6px;
            margin: 0.5rem 0;
            border-left: 4px solid #667eea;
            background-color: #f8f9fa;
        }
        
        /* Убираем :hover эффекты которые могут мешать */
        .card:hover {
            transform: none;
        }
        
        .stButton>button:hover {
            transform: none;
        }
    </style>
    """, unsafe_allow_html=True)

# Применяем CSS
inject_custom_css()

# СОСТОЯНИЯ СЕССИИ
def initialize_session_state():
    """Инициализация состояния сессии"""
    if "username" not in st.session_state:
        st.session_state.update({
            "username": None,
            "role": None,
            "mode": "login",
            "page": "home",
            "notifications": [],
            "last_login": None,
            "creating_test": False,
            "test_questions": [],
            "test_started": False,
            "current_test": None,
            "test_start_time": None,
            "last_test_result": None
        })

initialize_session_state()

# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
def show_sidebar():
    """Боковая панель с информацией"""
    with st.sidebar:
        st.markdown(" ## 🎓 DB Learn - Siberian Professional College")
        
        if st.session_state.username:
            role_emoji = "👨‍🏫" if st.session_state.role == "Преподаватель" else "🎓"
            st.markdown(f"### {role_emoji} {st.session_state.username}")
            st.markdown(f"**Роль:** {st.session_state.role}")
            
            if st.session_state.get("last_login"):
                st.markdown(f"**Последний вход:** {st.session_state.last_login}")
        
        if st.session_state.username:
            if st.button("🚪 Выход", use_container_width=True):
                logout()
                
        st.markdown("---")
        st.markdown("""
            <div style='text-align: center; color: var(--text-color);'>
                <small>© 2025 БПОУ ОО «Сибирский профессиональный колледж»</small><br>
                <small>Преподаватель/Разработчик: <strong>Стариков А.В.</strong></small>
            </div>
            """, unsafe_allow_html=True)
        
# ФОРМА ВХОДА
def show_login_form():
    """Форма входа в систему"""
    col_img, col_form = st.columns([1, 2])

    with col_img:
        st.markdown("""
        <div style='text-align: center; padding: 2rem 0;'>
            <h1 style='font-size: 4rem;'>👋</h1>
            <h2 style='color: var(--text-color);'>Добро пожаловать!</h2>
        </div>
        """, unsafe_allow_html=True)

    with col_form:
        st.markdown("### 🔐 Авторизация")

        with st.form("login_form", clear_on_submit=False):
            username = st.text_input(
                "👤 Логин",
                placeholder="Введите ваш логин",
                help="Введите ваш уникальный идентификатор",
                key="login_username"
            )
            password = st.text_input(
                "🔒 Пароль",
                type="password",
                placeholder="Введите ваш пароль",
                help="Введите ваш секретный пароль",
                key="login_password"
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
                    "👀 Гость",
                    use_container_width=True
                )

            if login_btn:
                handle_login(username, password)
            elif reg_btn:
                st.session_state.mode = "register"
                st.rerun()
            elif guest_btn:
                st.info("👋 Гостевой доступ в разработке")

        st.markdown("---")
        st.markdown("""
        <div style='text-align: center; color: var(--text-color);'>
            <small>Нет аккаунта? Зарегистрируйтесь для доступа к материалам</small>
        </div>
        """, unsafe_allow_html=True)

def handle_login(username: str, password: str):
    """Обработка входа пользователя"""
    if not username or not password:
        st.warning("⚠️ Пожалуйста, заполните все поля")
        return
        
    with st.spinner("🔐 Проверка учетных данных..."):
        time.sleep(0.5)  # Короткая задержка для UX
        if authenticate_user(username, password):
            st.session_state.update({
                "username": username,
                "role": get_user_role(username),
                "last_login": datetime.now().strftime("%d.%m.%Y %H:%M"),
                "mode": "login"
            })
            st.success("✅ Успешный вход! Перенаправляем...")
            time.sleep(1)
            st.rerun()
        else:
            st.error("❌ Неверный логин или пароль")

# ФОРМА РЕГИСТРАЦИИ
def show_register_form():
    """Форма регистрации нового пользователя"""
    st.markdown("### 📝 Регистрация нового пользователя")
    st.info("Заполните все поля для создания учетной записи")

    with st.form("register_form", clear_on_submit=False):
        col1, col2 = st.columns(2)

        with col1:
            username = st.text_input(
                "👤 Логин *",
                placeholder="Придумайте уникальный логин",
                help="Минимум 3 символа",
                key="reg_username"
            )
            full_name = st.text_input(
                "👤 Полное имя *",
                placeholder="Иванов Иван Иванович",
                key="reg_full_name"
            )
            group = st.text_input(
                "👥 Группа *",
                placeholder="Укажите свою группу",
                key="reg_group"
            )

        with col2:
            password = st.text_input(
                "🔒 Пароль *",
                type="password",
                placeholder="Создайте надежный пароль",
                help="Минимум 6 символов",
                key="reg_password"
            )
            confirm_password = st.text_input(
                "🔒 Подтверждение пароля *",
                type="password",
                placeholder="Повторите пароль",
                key="reg_confirm_password"
            )

        email = st.text_input(
            "📧 Email",
            placeholder="ivanov@example.com",
            help="Необязательно для заполнения",
            key="reg_email"
        )

        # Индикатор сложности пароля
        if password:
            show_password_strength(password)

        st.markdown("**По умолчанию все новые пользователи регистрируются как Студенты**")

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
            handle_registration(username, password, confirm_password, full_name, group, email)
        if back_btn:
            st.session_state.mode = "login"
            st.rerun()

def show_password_strength(password: str):
    """Показывает сложность пароля"""
    if len(password) >= 8 and any(c.isdigit() for c in password) and any(c.isalpha() for c in password):
        strength = "🟢 Надежный"
    elif len(password) >= 6:
        strength = "🟡 Средний"
    else:
        strength = "🔴 Слабый"
    st.write(f"**Сложность пароля:** {strength}")

def handle_registration(username: str, password: str, confirm_password: str, 
                       full_name: str, group: str, email: str):
    """Обработка регистрации пользователя"""
    if not all([username, password, confirm_password, full_name, group]):
        st.error("❌ Пожалуйста, заполните все обязательные поля (отмечены *)")
        return
        
    if password != confirm_password:
        st.error("❌ Пароли не совпадают")
        return
        
    if len(password) < 6:
        st.error("❌ Пароль должен содержать минимум 6 символов")
        return

    success = add_user(
        username=username,
        password=password, 
        role="Студент",
        full_name=full_name,
        group_name=group,
        email=email if email else None
    )

    if success:
        st.success("🎉 Регистрация успешна! Теперь войдите в систему.")
        time.sleep(2)
        st.session_state.mode = "login"
        st.rerun()
    else:
        st.error("❌ Пользователь с таким логином уже существует")

# ПАНЕЛЬ ПРЕПОДАВАТЕЛЯ
def show_teacher_panel():
    """Основная панель преподавателя"""
    st.markdown(f"### 👨‍🏫 Панель преподавателя")
    st.markdown(f"**Добро пожаловать, {st.session_state.username}!** Рады видеть вас снова.")
    
    # Основные разделы
    tab1, tab2, tab3, tab4 = st.tabs([
        "📈 Дашборд", "👥 Студенты", "🧩 Тесты", "⚙️ Настройки"
    ])

    with tab1:
        show_teacher_dashboard()
    with tab2:
        show_students_management()
    with tab3:
        show_tests_management()
    with tab4:
        show_teacher_settings()

def show_teacher_dashboard():
    """Дашборд преподавателя с аналитикой"""
    st.markdown("### 📊 Обзор системы")
    
    # Основные метрики
    dashboard_stats = get_teacher_dashboard_stats(st.session_state.username)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("🧩 Создано тестов", dashboard_stats['total_tests'])
    with col2:
        st.metric("👥 Всего студентов", dashboard_stats['total_students'])
    with col3:
        st.metric("📊 Групп", dashboard_stats['total_groups'])
    
    # Вкладки аналитики
    tab1, tab2, tab3, tab4 = st.tabs([
        "📈 Общая статистика", "👥 По группам", "🧩 Аналитика тестов", "🏆 Рейтинг"
    ])
    
    with tab1:
        show_general_statistics()
    with tab2:
        show_group_analytics()
    with tab3:
        show_test_analytics_interface()
    with tab4:
        show_student_ranking()

def show_general_statistics():
    """Общая статистика системы"""
    st.markdown("#### 📈 Активность системы")
    st.info("📊 Графики активности появятся после накопления данных")
    
    st.markdown("#### 👥 Статистика по группам")
    try:
        students = get_all_students()
        groups = list(set([student["group"] for student in students if student["group"]]))
        
        for group in groups:
            stats = get_group_statistics(group)
            if stats:
                with st.container():
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric(f"👥 {group}", f"{stats['student_count']} студентов")
                    with col2:
                        st.metric("📊 Средний %", f"{stats['avg_success_rate']}%")
                    with col3:
                        st.metric("🧩 Тестов", stats['total_tests'])
                    with col4:
                        st.metric("🔄 Попыток", stats['total_attempts'])
                    
                    if stats['grade_distribution']:
                        st.write("**Распределение оценок:**")
                        for grade_range, count in stats['grade_distribution'].items():
                            percentage = (count / stats['total_attempts'] * 100) if stats['total_attempts'] > 0 else 0
                            st.write(f"{grade_range}: {count} ({percentage:.1f}%)")
                            st.progress(percentage / 100)
                    
                    st.markdown("---")
    except Exception as e:
        st.error(f"Ошибка при загрузке статистики: {e}")

def show_group_analytics():
    """Детальная аналитика по группам"""
    st.markdown("#### 👥 Детальная аналитика по группам")
    
    students = get_all_students()
    groups = list(set([student["group"] for student in students if student["group"]]))
    
    if not groups:
        st.info("📭 Нет данных о группах")
        return
    
    selected_group = st.selectbox("Выберите группу для анализа:", groups, key="group_analytics_select")
    
    if selected_group:
        stats = get_group_statistics(selected_group)
        if stats:
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("##### 📊 Основные метрики")
                st.write(f"**Студентов в группе:** {stats['student_count']}")
                st.write(f"**Всего тестов пройдено:** {stats['total_tests']}")
                st.write(f"**Всего попыток:** {stats['total_attempts']}")
                st.write(f"**Средний процент успеха:** {stats['avg_success_rate']}%")
                st.write(f"**Лучший результат:** {stats['max_success_rate']}%")
                st.write(f"**Худший результат:** {stats['min_success_rate']}%")
            
            with col2:
                st.markdown("##### 📈 Распределение оценок")
                if stats['grade_distribution']:
                    grades = list(stats['grade_distribution'].keys())
                    counts = list(stats['grade_distribution'].values())
                    fig = px.bar(x=grades, y=counts, title=f"Распределение оценок - {selected_group}")
                    st.plotly_chart(fig, use_container_width=True)

def show_test_analytics_interface():
    """Интерфейс аналитики тестов"""
    st.markdown("#### 🧩 Аналитика тестов")
    
    tests = get_teacher_tests(st.session_state.username)
    if not tests:
        st.info("📭 У вас пока нет созданных тестов")
        return
    
    test_titles = [f"{test['id']}: {test['title']}" for test in tests]
    selected_test_title = st.selectbox("Выберите тест для анализа:", test_titles, key="test_analytics_select")
    
    if selected_test_title:
        test_id = int(selected_test_title.split(":")[0])
        analytics = get_test_analytics(test_id)
        
        if analytics and 'title' in analytics:
            st.markdown(f"##### 📝 {analytics['title']}")
            if analytics.get('description'):
                st.write(f"_{analytics['description']}_")
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("🔄 Попыток", analytics.get('total_attempts', 0))
            with col2:
                st.metric("📊 Средний балл", f"{analytics.get('avg_score', 0):.1f}")
            with col3:
                st.metric("⭐ Средний %", f"{analytics.get('avg_success_rate', 0)}%")
            with col4:
                st.metric("❓ Вопросов", analytics.get('question_count', 0))
            
            if analytics.get('total_attempts', 0) > 0:
                show_detailed_test_analytics(analytics)
            else:
                st.info("🎯 Этот тест еще никто не прошел")

def show_detailed_test_analytics(analytics: dict):
    """Показывает детальную аналитику теста"""
    # Распределение оценок
    st.markdown("##### 📈 Распределение оценок")
    grade_distribution = analytics.get('grade_distribution', {})
    if grade_distribution:
        grades = list(grade_distribution.keys())
        counts = list(grade_distribution.values())
        fig = px.pie(values=counts, names=grades, title="Распределение результатов")
        st.plotly_chart(fig, use_container_width=True)
        
        st.write("**Детальное распределение:**")
        total_attempts = analytics.get('total_attempts', 1)
        for grade_range, count in grade_distribution.items():
            percentage = (count / total_attempts * 100)
            st.write(f"{grade_range}: {count} студентов ({percentage:.1f}%)")
            st.progress(percentage / 100)
    else:
        st.info("📭 Нет данных о распределении оценок")
    
    # Дополнительная статистика
    st.markdown("##### 📊 Дополнительная статистика")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("🎯 Лучший результат", f"{analytics.get('max_score_achieved', 0)} баллов")
    with col2:
        st.metric("📉 Худший результат", f"{analytics.get('min_score_achieved', 0)} баллов")
    with col3:
        st.metric("⏱️ Среднее время", f"{analytics.get('avg_time_spent', 0)} сек")

def show_student_ranking():
    """Рейтинг студентов"""
    st.markdown("#### 🏆 Рейтинг студентов")
    
    ranking = get_student_ranking()
    if not ranking:
        st.info("📭 Пока нет данных для рейтинга")
        return
    
    st.markdown("##### Топ-20 студентов по успеваемости")
    for student in ranking:
        with st.container():
            col1, col2, col3, col4, col5 = st.columns([1, 3, 2, 2, 2])
            with col1:
                emoji = "🥇" if student['rank'] == 1 else "🥈" if student['rank'] == 2 else "🥉" if student['rank'] == 3 else "🏅"
                st.write(f"**{emoji} #{student['rank']}**")
            with col2:
                st.write(f"**{student['full_name']}**")
                st.write(f"Группа: {student['group']}")
            with col3:
                st.write(f"📊 {student['avg_success_rate']}%")
            with col4:
                st.write(f"🧩 {student['tests_completed']} тестов")
            with col5:
                st.write(f"⭐ {student['total_points']} баллов")
            st.markdown("---")

def show_students_management():
    """Управление студентами"""
    st.markdown("### 👥 Управление студентами")

    # Поиск и фильтры
    col1, col2 = st.columns([2, 1])
    with col1:
        search = st.text_input("🔍 Поиск студента по имени", key="student_search")
    with col2:
        students = get_all_students()
        groups = list(set([student["group"] for student in students if student["group"]]))
        groups.insert(0, "Все")
        filter_group = st.selectbox("Группа", groups, key="group_filter")

    if students:
        # Фильтрация студентов
        filtered_students = [
            student for student in students
            if (not search or search.lower() in student["full_name"].lower() or search.lower() in student["username"].lower())
            and (filter_group == "Все" or student["group"] == filter_group)
        ]
        
        st.success(f"🎯 Найдено студентов: {len(filtered_students)}")

        # Отображение студентов
        for i, student in enumerate(filtered_students):
            with st.container():
                col1, col2, col3 = st.columns([3, 2, 1])
                with col1:
                    st.write(f"### 🎓 {student['full_name']}")
                    st.write(f"**Логин:** {student['username']}")
                    st.write(f"**Группа:** {student['group']}")
                    if student['email']:
                        st.write(f"**Email:** {student['email']}")
                with col2:
                    st.write("**📊 Успеваемость**")
                    st.write("Тестов пройдено: 0")  # TODO: Реальная статистика
                    st.write("Средний балл: 0.0")
                with col3:
                    if st.button("👁️ Подробнее", key=f"view_{i}"):
                        st.session_state[f"view_student_{i}"] = not st.session_state.get(f"view_student_{i}", False)
                
                if st.session_state.get(f"view_student_{i}"):
                    with st.expander(f"📊 Детальная информация", expanded=True):
                        show_student_details(student, i)
                st.markdown("---")
    else:
        st.warning("📭 Пока нет зарегистрированных студентов")

def show_student_details(student: dict, index: int):
    """Детальная информация о студенте"""
    col1, col2 = st.columns(2)
    with col1:
        st.write("**📊 Статистика обучения**")
        st.write("Пройдено тестов: 0")
        st.write("Средний балл: 0.0")
        st.write("Лучший результат: 0%")
        st.write("Активность: низкая")
    with col2:
        st.write("**🎯 Последняя активность**")
        st.write("Последний тест: нет данных")
        st.write("Дата последнего входа: нет данных")
        st.write("Всего времени в системе: нет данных")
    
    st.write("**📈 История тестов**")
    st.info("Здесь будет история прохождения тестов")

def show_tests_management():
    """Управление тестами"""
    st.markdown("### 🧩 Управление тестами")

    col1, col2 = st.columns([3, 1])
    with col1:
        st.subheader("📋 Мои тесты")
    with col2:
        if st.button("➕ Создать тест", use_container_width=True):
            st.session_state.creating_test = True

    show_existing_tests()
    
    # Форма создания теста показывается только при явном запросе
    if st.session_state.get("creating_test"):
        show_create_test_form()

def show_existing_tests():
    """Показать существующие тесты"""
    try:
        tests = get_teacher_tests(st.session_state.username)
        if not tests:
            st.info("📭 У вас пока нет созданных тестов")
            return

        for test in tests:
            with st.container():
                col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
                with col1:
                    status = "🟢 Активен" if test['is_active'] else "🔴 Неактивен"
                    st.write(f"**{test['title']}** - {status}")
                    st.write(f"_{test['description']}_")
                with col2:
                    st.write(f"⏱️ {test['time_limit']} мин")
                with col3:
                    st.write(f"🔄 {test['max_attempts']} попыт.")
                with col4:
                    if st.button("👁️ Просмотр", key=f"view_test_{test['id']}"):
                        st.session_state[f"viewing_test_{test['id']}"] = not st.session_state.get(f"viewing_test_{test['id']}", False)
                
                if st.session_state.get(f"viewing_test_{test['id']}"):
                    show_test_details(test)
                st.markdown("---")
    except Exception as e:
        st.error(f"Ошибка при загрузке тестов: {e}")

def show_create_test_form():
    """Форма создания теста"""
    st.markdown("---")
    st.markdown("### 📝 Создание нового теста")
    
    with st.form("create_test_form", clear_on_submit=False):
        # Основная информация
        col1, col2 = st.columns(2)
        with col1:
            test_title = st.text_input("Название теста *", placeholder="Введение в базы данных")
            time_limit = st.number_input("Лимит времени (минут) *", min_value=5, max_value=180, value=60)
        with col2:
            test_description = st.text_area("Описание теста", placeholder="Тест охватывает основные понятия БД...", height=100)
            max_attempts = st.number_input("Количество попыток", min_value=1, max_value=10, value=1)
        
        # Настройки
        col1, col2 = st.columns(2)
        with col1:
            shuffle_questions = st.checkbox("Перемешивать вопросы", value=True)
            show_results = st.checkbox("Показывать результаты после завершения", value=False)
        with col2:
            is_active = st.checkbox("Сразу активировать тест", value=True)
        
        st.markdown("---")
        st.markdown("### ❓ Вопросы теста")
        
        # Управление вопросами
        show_questions_management()
        
        # Кнопки управления
        col1, col2 = st.columns(2)
        with col1:
            if st.form_submit_button("✅ Создать тест", use_container_width=True):
                if validate_test_data(test_title, time_limit):
                    create_new_test(test_title, test_description, time_limit, max_attempts, shuffle_questions, show_results, is_active)
        with col2:
            if st.form_submit_button("❌ Отмена", use_container_width=True):
                st.session_state.creating_test = False
                cleanup_test_creation_state()

def show_questions_management():
    """Управление вопросами теста"""
    # Инициализация списка вопросов
    if "test_questions" not in st.session_state:
        st.session_state.test_questions = []
    
    # Показать существующие вопросы
    if st.session_state.test_questions:
        st.markdown("#### Добавленные вопросы:")
        for i, question in enumerate(st.session_state.test_questions, 1):
            with st.container():
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.write(f"**{i}. {question['text']}** (Тип: {question['type']}, Баллы: {question['points']})")
                with col2:
                    if st.button("❌ Удалить", key=f"del_q_{i}"):
                        st.session_state.test_questions.pop(i-1)
                        st.rerun()
    
    # Добавление нового вопроса
    st.markdown("#### Добавить новый вопрос:")
    show_question_creator()

def show_question_creator():
    """Создатель вопроса"""
    question_type = st.selectbox(
        "Тип вопроса",
        ["single_choice", "multiple_choice", "text"],
        format_func=lambda x: {
            "single_choice": "Один вариант ответа", 
            "multiple_choice": "Несколько вариантов", 
            "text": "Текстовый ответ"
        }[x],
        key="question_type_select"
    )
    
    with st.form("add_question_form", clear_on_submit=True):
        question_text = st.text_area("Текст вопроса *", placeholder="Введите вопрос...")
        points = st.number_input("Баллы за вопрос", min_value=1, max_value=10, value=1)
        
        correct_answers = []
        if question_type in ["single_choice", "multiple_choice"]:
            correct_answers = handle_choice_question(question_type)
        else:
            correct_answers = handle_text_question()
        
        if st.form_submit_button("💾 Добавить вопрос", use_container_width=True):
            if validate_question_data(question_text, question_type, correct_answers):
                add_question_to_session(question_text, question_type, points, correct_answers)
                st.success("✅ Вопрос добавлен!")
                st.rerun()

def handle_choice_question(question_type: str) -> list:
    """Обрабатывает вопросы с выбором ответа"""
    st.markdown("**Варианты ответов:**")
    
    # Инициализация вариантов
    options_key = f"options_{question_type}"
    if options_key not in st.session_state:
        st.session_state[options_key] = [""]
    
    options = st.session_state[options_key]
    
    # Отображение вариантов
    for i in range(len(options)):
        col1, col2 = st.columns([4, 1])
        with col1:
            options[i] = st.text_input(f"Вариант {i+1}", value=options[i], 
                                     placeholder=f"Введите вариант {i+1}", key=f"option_{i}")
        with col2:
            if i > 0 and st.form_submit_button("❌", key=f"del_opt_{i}"):
                options.pop(i)
                st.rerun()
    
    if st.form_submit_button("➕ Добавить вариант", key="add_option"):
        options.append("")
        st.rerun()
    
    # Выбор правильных ответов
    st.markdown("**Правильные ответы:**")
    valid_options = [opt for opt in options if opt.strip()]
    
    if not valid_options:
        st.warning("Добавьте варианты ответов")
        return []
    
    if question_type == "single_choice":
        correct_index = st.radio("Выберите правильный вариант:", range(len(valid_options)),
                               format_func=lambda x: valid_options[x])
        return [valid_options[correct_index]]
    else:
        correct_indices = st.multiselect("Выберите правильные варианты:", range(len(valid_options)),
                                       format_func=lambda x: valid_options[x])
        return [valid_options[i] for i in correct_indices]

def handle_text_question() -> list:
    """Обрабатывает текстовые вопросы"""
    correct_answer = st.text_input("Правильный ответ *", placeholder="Введите правильный ответ...")
    return [correct_answer] if correct_answer.strip() else []

def add_question_to_session(question_text: str, question_type: str, points: int, correct_answers: list):
    """Добавляет вопрос в сессию"""
    question_data = {
        "text": question_text,
        "type": question_type,
        "points": points,
        "options": st.session_state.get(f"options_{question_type}", []).copy() if question_type in ["single_choice", "multiple_choice"] else [],
        "correct_answers": correct_answers
    }
    st.session_state.test_questions.append(question_data)
    
    # Очистка временных данных
    options_key = f"options_{question_type}"
    if options_key in st.session_state:
        del st.session_state[options_key]

def validate_test_data(title: str, time_limit: int) -> bool:
    """Валидация данных теста"""
    if not title.strip():
        st.error("❌ Введите название теста")
        return False
    if time_limit < 1:
        st.error("❌ Лимит времени должен быть положительным")
        return False
    if not st.session_state.get("test_questions"):
        st.error("❌ Добавьте хотя бы один вопрос")
        return False
    return True

def validate_question_data(question_text: str, question_type: str, correct_answers: list) -> bool:
    """Валидация данных вопроса"""
    if not question_text.strip():
        st.error("❌ Введите текст вопроса")
        return False
    
    if question_type in ["single_choice", "multiple_choice"]:
        options_key = f"options_{question_type}"
        if options_key not in st.session_state:
            st.error("❌ Добавьте варианты ответов")
            return False
            
        options = st.session_state[options_key]
        valid_options = [opt for opt in options if opt.strip()]
        
        if len(valid_options) < 2:
            st.error("❌ Нужно хотя бы 2 варианта ответа")
            return False
            
        if not correct_answers:
            st.error("❌ Выберите правильный ответ")
            return False
    
    else:  # text question
        if not correct_answers or not correct_answers[0].strip():
            st.error("❌ Введите правильный ответ")
            return False
    
    return True

def create_new_test(title: str, description: str, time_limit: int, max_attempts: int,
                   shuffle_questions: bool, show_results: bool, is_active: bool):
    """Создание нового теста"""
    try:
        test_id = create_test(
            title=title,
            description=description,
            time_limit=time_limit,
            max_attempts=max_attempts,
            created_by=st.session_state.username
        )
        
        # Добавляем вопросы
        for i, question_data in enumerate(st.session_state.test_questions):
            create_secure_question(
                test_id=test_id,
                question_text=question_data["text"],
                options=question_data["options"],
                correct_answers=question_data["correct_answers"],
                question_type=question_data["type"],
                points=question_data["points"],
                question_order=i
            )
        
        st.success(f"🎉 Тест '{title}' успешно создан! ID: {test_id}")
        cleanup_test_creation_state()
        st.rerun()
        
    except Exception as e:
        st.error(f"❌ Ошибка при создании теста: {e}")

def cleanup_test_creation_state():
    """Очистка состояния создания теста"""
    st.session_state.creating_test = False
    keys_to_remove = [key for key in st.session_state.keys() 
                     if key.startswith(('test_questions', 'options_', 'test_', 'question_'))]
    for key in keys_to_remove:
        if key in st.session_state:
            del st.session_state[key]

def show_test_details(test: dict):
    """Детальная информация о тесте"""
    with st.expander(f"📊 Детали теста", expanded=True):
        try:
            questions = get_test_questions(test['id'])
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("❓ Вопросов", len(questions))
            with col2:
                st.metric("⭐ Всего баллов", sum(q['points'] for q in questions))
            with col3:
                st.metric("👥 Прошли", "0")  # TODO: Реальная статистика
            
            st.markdown("#### Вопросы:")
            for i, question in enumerate(questions, 1):
                st.write(f"**{i}. {question['question_text']}**")
                st.write(f"Тип: {question['question_type']} | Баллы: {question['points']}")
                
                if question['options']:
                    st.write("Варианты:")
                    for opt in question['options']:
                        st.write(f" - {opt}")
                
                st.markdown("---")
        except Exception as e:
            st.error(f"Ошибка при загрузке вопросов: {e}")

def show_teacher_settings():
    """Настройки преподавателя"""
    st.markdown("### ⚙️ Настройки преподавателя")
    
    with st.form("teacher_settings"):
        st.subheader("🎨 Внешний вид")
        
        col1, col2 = st.columns(2)
        with col1:
            theme = st.selectbox("Тема интерфейса", ["Светлая", "Темная", "Авто"])
            language = st.selectbox("Язык интерфейса", ["Русский", "English"])
        
        with col2:
            font_size = st.slider("Размер шрифта", 12, 24, 16)
            compact_mode = st.checkbox("Компактный режим")
        
        if st.form_submit_button("💾 Сохранить настройки", use_container_width=True):
            st.success("✅ Настройки успешно сохранены!")

# ПАНЕЛЬ СТУДЕНТА
def show_student_panel():
    """Основная панель студента"""
    student_data = get_student_data(st.session_state.username)
    
    st.markdown(f"### 🎓 Добро пожаловать, {student_data['full_name']}!")
    
    # Основные метрики
    test_results = get_test_results(st.session_state.username)
    completed_tests = len(test_results)
    avg_score = sum(r['score'] for r in test_results) / len(test_results) if test_results else 0
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("🧩 Пройдено тестов", completed_tests)
    with col2:
        st.metric("⭐ Средний балл", f"{avg_score:.1f}")
    with col3:
        st.metric("👥 Группа", student_data['group'])
    
    st.markdown("---")
    
    # Вкладки
    tab1, tab2, tab3 = st.tabs(["🧩 Доступные тесты", "📊 Мои результаты", "📈 Мой прогресс"])
    
    with tab1:
        show_available_tests_student()
    with tab2:
        show_student_results()
    with tab3:
        show_student_progress_interface()

def show_available_tests_student():
    """Доступные тесты для студента"""
    st.markdown("### 🧩 Доступные тесты")
    
    try:
        available_tests = get_available_tests(st.session_state.username)
        
        if not available_tests:
            st.info("🎉 Отличная работа! На данный момент нет доступных тестов.")
            return
        
        for test in available_tests:
            with st.container():
                col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
                with col1:
                    st.write(f"**{test['title']}**")
                    st.write(f"_{test['description']}_")
                    st.write(f"Попытка: {test['current_attempt']} из {test['max_attempts']}")
                with col2:
                    questions = get_test_questions(test['id'])
                    st.write(f"❓ {len(questions)} вопр.")
                with col3:
                    st.write(f"⏱️ {test['time_limit']} мин.")
                with col4:
                    if st.button("Начать тест", key=f"start_test_{test['id']}"):
                        st.session_state.update({
                            "current_test": test,
                            "test_started": True,
                            "test_start_time": time.time()
                        })
                        st.rerun()
                st.markdown("---")
    except Exception as e:
        st.error(f"Ошибка при загрузке тестов: {e}")

def show_student_results():
    """Результаты студента"""
    st.markdown("### 📊 Мои результаты")
    
    try:
        results = get_test_results(st.session_state.username)
        
        if not results:
            st.info("📭 Вы еще не прошли ни одного теста")
            return
        
        for result in results:
            percentage = (result['score'] / result['max_score']) * 100
            color = "🟢" if percentage >= 80 else "🟡" if percentage >= 60 else "🔴"
            
            with st.container():
                col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
                with col1:
                    st.write(f"**{result['test_title']}**")
                    st.write(f"Попытка #{result['attempt_number']}")
                with col2:
                    st.write(f"{color} {result['score']}/{result['max_score']}")
                with col3:
                    st.write(f"📅 {result['completed_at'][:10]}")
                with col4:
                    st.write(f"⏱️ {result['time_spent']}с")
                st.markdown("---")
    except Exception as e:
        st.error(f"Ошибка при загрузке результатов: {e}")

def show_student_progress_interface():
    """Прогресс студента"""
    st.markdown("### 📈 Мой прогресс")
    
    try:
        progress_data = get_student_progress(st.session_state.username)
        
        if not progress_data:
            st.info("📭 У вас пока нет данных о прогрессе")
            return
        
        # График прогресса
        dates = [item['date'] for item in progress_data]
        daily_avg = [item['daily_avg'] for item in progress_data]
        
        fig = px.line(x=dates, y=daily_avg, title="Прогресс успеваемости",
                     labels={'x': 'Дата', 'y': 'Средний процент успеха (%)'})
        st.plotly_chart(fig, use_container_width=True)
        
        # Детальная статистика
        st.markdown("#### 📊 Детальная статистика")
        for progress in progress_data:
            with st.container():
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.write(f"**📅 {progress['date']}**")
                with col2:
                    st.write(f"📊 {progress['daily_avg']}%")
                with col3:
                    st.write(f"🧩 {progress['tests_taken']} тестов")
                st.markdown("---")
    except Exception as e:
        st.error(f"Ошибка при загрузке прогресса: {e}")

# ИНТЕРФЕЙС ПРОХОЖДЕНИЯ ТЕСТА
def show_test_interface():
    """Интерфейс прохождения теста"""
    if not st.session_state.get("test_started"):
        return
    
    test = st.session_state.current_test
    questions = get_test_questions(test['id'])
    
    # Таймер
    elapsed_time = time.time() - st.session_state.test_start_time
    remaining_time = (test['time_limit'] * 60) - elapsed_time
    
    if remaining_time <= 0:
        handle_test_timeout(test, int(elapsed_time))
        return
    
    show_test_timer(remaining_time)
    show_test_questions(test, questions, elapsed_time)

def handle_test_timeout(test: dict, elapsed_time: int):
    """Обработка истечения времени теста"""
    st.error("⏰ Время вышло! Тест автоматически завершен.")
    submit_test_answers(test['id'], st.session_state.username, {}, elapsed_time)
    cleanup_test_session()
    st.rerun()

def show_test_timer(remaining_time: int):
    """Показывает таймер теста"""
    minutes = int(remaining_time // 60)
    seconds = int(remaining_time % 60)
    st.warning(f"⏰ Осталось времени: {minutes:02d}:{seconds:02d}")

def show_test_questions(test: dict, questions: list, elapsed_time: int):
    """Показывает вопросы теста"""
    with st.form("test_form"):
        st.markdown(f"### {test['title']}")
        st.markdown(f"_{test['description']}_")
        
        answers = collect_answers(questions)
        
        # Кнопки управления
        col1, col2 = st.columns([1, 1])
        with col1:
            submitted = st.form_submit_button("✅ Завершить тест", use_container_width=True)
        with col2:
            if st.form_submit_button("❌ Выйти", use_container_width=True):
                cleanup_test_session()
                st.rerun()
        
        if submitted:
            handle_test_submission(test, answers, int(elapsed_time))

def collect_answers(questions: list) -> dict:
    """Собирает ответы на вопросы"""
    answers = {}
    for i, question in enumerate(questions, 1):
        st.markdown("---")
        st.markdown(f"**Вопрос {i}** ({question['points']} баллов)")
        st.markdown(question['question_text'])
        
        if question['question_type'] == 'single_choice':
            answer = st.radio("Выберите вариант:", question['options'], 
                            key=f"q_{question['id']}", label_visibility="collapsed")
            answers[str(question['id'])] = answer
        elif question['question_type'] == 'multiple_choice':
            selected = st.multiselect("Выберите варианты:", question['options'],
                                    key=f"q_{question['id']}", label_visibility="collapsed")
            answers[str(question['id'])] = selected
        else:  # text
            answer = st.text_area("Введите ваш ответ:", key=f"q_{question['id']}", 
                                label_visibility="collapsed")
            answers[str(question['id'])] = answer
    return answers

def handle_test_submission(test: dict, answers: dict, elapsed_time: int):
    """Обрабатывает отправку теста"""
    score, max_score = submit_test_answers(test['id'], st.session_state.username, answers, elapsed_time)
    st.session_state.update({
        "test_started": False,
        "last_test_result": {
            'score': score,
            'max_score': max_score,
            'test_title': test['title']
        }
    })
    del st.session_state.current_test
    st.rerun()

def cleanup_test_session():
    """Очистка сессии теста"""
    st.session_state.test_started = False
    if "current_test" in st.session_state:
        del st.session_state.current_test

def show_test_result():
    """Показывает результаты теста"""
    if not st.session_state.get("last_test_result"):
        return
        
    result = st.session_state.last_test_result
    percentage = (result['score'] / result['max_score']) * 100
    
    st.balloons()
    st.success(f"🎉 Тест '{result['test_title']}' завершен!")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Набрано баллов", f"{result['score']}/{result['max_score']}")
    with col2:
        st.metric("Процент выполнения", f"{percentage:.1f}%")
    with col3:
        status = "✅ Сдано" if percentage >= 60 else "❌ Не сдано"
        st.metric("Результат", status)
    
    if st.button("Вернуться к списку тестов"):
        del st.session_state.last_test_result
        st.rerun()

# ВЫХОД ИЗ СИСТЕМЫ
def logout():
    """Выход из системы"""
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
    """Основная функция приложения"""
    show_sidebar()

    # Заголовок для неавторизованных пользователей
    if not st.session_state.username:
        st.markdown(
            '<h1 class="main-header">🛢️ Образовательная платформа: Разработка, администрирование и защита баз данных</h1>', 
            unsafe_allow_html=True
        )
        st.markdown("---")

    # Логика отображения контента
    if st.session_state.username:
        handle_authenticated_user()
    else:
        handle_unauthenticated_user()

def handle_authenticated_user():
    """Обработка авторизованного пользователя"""
    if (st.session_state.role == "Студент" and st.session_state.get("test_started")):
        show_test_interface()
    elif st.session_state.get("last_test_result"):
        show_test_result()
    else:
        if st.session_state.role == "Преподаватель":
            show_teacher_panel()
        else:
            show_student_panel()

def handle_unauthenticated_user():
    """Обработка неавторизованного пользователя"""
    if st.session_state.mode == "login":
        show_login_form()
    else:
        show_register_form()

if __name__ == "__main__":
    main()
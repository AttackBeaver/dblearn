import sys
import os
sys.path.append(os.path.dirname(__file__))

from data.db_manager import create_test, create_secure_question

def add_sample_tests():
    """Добавляет примеры тестов по базам данных напрямую в БД"""
    
    print("🚀 Начинаем добавление тестовых данных...")
    
    # Тест 1: Основы баз данных
    test1_id = create_test(
        title="Основы баз данных",
        description="Тест по основным понятиям и принципам работы с базами данных",
        time_limit=45,
        max_attempts=3,
        created_by="teacher"
    )
    
    # Вопросы для теста 1
    create_secure_question(
        test_id=test1_id,
        question_text="Что такое СУБД?",
        question_type="single_choice",
        options=[
            "Система управления базами данных",
            "Сетевой узел баз данных", 
            "Структурный уровень баз данных",
            "Сервер управления базами"
        ],
        correct_answers=["Система управления базами данных"],
        points=2,
        question_order=1
    )
    
    create_secure_question(
        test_id=test1_id,
        question_text="Какие основные операции можно выполнять с данными в БД?",
        question_type="multiple_choice",
        options=[
            "SELECT (выборка)",
            "INSERT (вставка)",
            "DELETE (удаление)",
            "UPDATE (обновление)"
        ],
        correct_answers=["SELECT (выборка)", "INSERT (вставка)", "DELETE (удаление)", "UPDATE (обновление)"],
        points=3,
        question_order=2
    )
    
    create_secure_question(
        test_id=test1_id,
        question_text="Что означает принцип ACID в транзакциях?",
        question_type="text",
        options=[],
        correct_answers=["atomicity consistency isolation durability"],
        points=5,
        question_order=3
    )
    
    create_secure_question(
        test_id=test1_id,
        question_text="Какая из перечисленных СУБД является реляционной?",
        question_type="single_choice",
        options=[
            "MySQL",
            "MongoDB",
            "Redis",
            "Cassandra"
        ],
        correct_answers=["MySQL"],
        points=2,
        question_order=4
    )
    
    # Тест 2: SQL основы
    test2_id = create_test(
        title="SQL основы",
        description="Основные команды и синтаксис языка SQL",
        time_limit=60,
        max_attempts=2,
        created_by="teacher"
    )
    
    create_secure_question(
        test_id=test2_id,
        question_text="Какая команда используется для выборки данных?",
        question_type="single_choice",
        options=["GET", "SELECT", "FETCH", "EXTRACT"],
        correct_answers=["SELECT"],
        points=2,
        question_order=1
    )
    
    create_secure_question(
        test_id=test2_id,
        question_text="Для чего используется команда WHERE?",
        question_type="single_choice",
        options=[
            "Для сортировки результатов",
            "Для фильтрации записей",
            "Для объединения таблиц",
            "Для группировки данных"
        ],
        correct_answers=["Для фильтрации записей"],
        points=2,
        question_order=2
    )
    
    create_secure_question(
        test_id=test2_id,
        question_text="Какие команды относятся к DML (Data Manipulation Language)?",
        question_type="multiple_choice",
        options=[
            "CREATE",
            "SELECT",
            "INSERT", 
            "UPDATE",
            "DELETE"
        ],
        correct_answers=["SELECT", "INSERT", "UPDATE", "DELETE"],
        points=4,
        question_order=3
    )
    
    create_secure_question(
        test_id=test2_id,
        question_text="Как создать простой SQL запрос для выборки всех полей из таблицы 'users'?",
        question_type="text",
        options=[],
        correct_answers=["select * from users"],
        points=3,
        question_order=4
    )
    
    # Тест 3: Нормализация баз данных
    test3_id = create_test(
        title="Нормализация баз данных",
        description="Принципы нормализации и нормальные формы",
        time_limit=50,
        max_attempts=2,
        created_by="teacher"
    )
    
    create_secure_question(
        test_id=test3_id,
        question_text="Что такое первая нормальная форма (1NF)?",
        question_type="single_choice",
        options=[
            "Все атрибуты атомарны и нет повторяющихся групп",
            "Все зависимости от первичного ключа полные",
            "Нет транзитивных зависимостей",
            "Все вышеперечисленное"
        ],
        correct_answers=["Все атрибуты атомарны и нет повторяющихся групп"],
        points=3,
        question_order=1
    )
    
    create_secure_question(
        test_id=test3_id,
        question_text="Какие нормальные формы вы знаете?",
        question_type="multiple_choice",
        options=["1NF", "2NF", "3NF", "4NF", "5NF", "6NF"],
        correct_answers=["1NF", "2NF", "3NF", "4NF", "5NF"],
        points=4,
        question_order=2
    )
    
    create_secure_question(
        test_id=test3_id,
        question_text="Вторая нормальная форма требует:",
        question_type="single_choice",
        options=[
            "Чтобы таблица была в 1NF",
            "Чтобы все неключевые атрибуты полностью зависели от первичного ключа",
            "Чтобы не было транзитивных зависимостей",
            "Первый и второй варианты"
        ],
        correct_answers=["Первый и второй варианты"],
        points=3,
        question_order=3
    )
    
    # Тест 4: Транзакции и безопасность
    test4_id = create_test(
        title="Транзакции и безопасность БД",
        description="Принципы работы транзакций, блокировок и безопасность данных",
        time_limit=40,
        max_attempts=1,
        created_by="teacher"
    )
    
    create_secure_question(
        test_id=test4_id,
        question_text="Что такое транзакция в базе данных?",
        question_type="single_choice",
        options=[
            "Единица работы с БД, которая должна быть выполнена полностью или не выполнена совсем",
            "Процесс создания резервной копии",
            "Метод оптимизации запросов",
            "Тип соединения таблиц"
        ],
        correct_answers=["Единица работы с БД, которая должна быть выполнена полностью или не выполнена совсем"],
        points=2,
        question_order=1
    )
    
    create_secure_question(
        test_id=test4_id,
        question_text="Какие свойства транзакций описывает ACID?",
        question_type="multiple_choice",
        options=[
            "Атомарность (Atomicity)",
            "Согласованность (Consistency)", 
            "Изолированность (Isolation)",
            "Долговечность (Durability)",
            "Доступность (Availability)"
        ],
        correct_answers=["Атомарность (Atomicity)", "Согласованность (Consistency)", "Изолированность (Isolation)", "Долговечность (Durability)"],
        points=4,
        question_order=2
    )
    
    create_secure_question(
        test_id=test4_id,
        question_text="Что такое SQL инъекция и как от нее защититься?",
        question_type="text",
        options=[],
        correct_answers=["использование параметризованных запросов"],
        points=5,
        question_order=3
    )
    
    print("✅ Тестовые данные успешно добавлены!")
    print(f"""
📊 Добавлены тесты:
   - ID {test1_id}: Основы баз данных (4 вопроса)
   - ID {test2_id}: SQL основы (4 вопроса) 
   - ID {test3_id}: Нормализация баз данных (3 вопроса)
   - ID {test4_id}: Транзакции и безопасность БД (3 вопроса)
   
🎯 Всего: 4 теста, 14 вопросов
   
Теперь вы можете:
1. Зайти как преподаватель (teacher/10209065)
2. Перейти в раздел '🧩 Тесты' 
3. Увидеть все созданные тесты
4. Назначить их студентам
    """)

def add_sample_students():
    """Добавляет тестовых студентов"""
    from data.db_manager import add_user
    
    sample_students = [
        {"username": "student1", "password": "123456", "full_name": "Иванов Иван", "group": "ИТ-21", "email": "ivanov@college.ru"},
        {"username": "student2", "password": "123456", "full_name": "Петрова Анна", "group": "ИТ-21", "email": "petrova@college.ru"},
        {"username": "student3", "password": "123456", "full_name": "Сидоров Алексей", "group": "ИТ-22", "email": "sidorov@college.ru"},
        {"username": "student4", "password": "123456", "full_name": "Кузнецова Мария", "group": "ИТ-22", "email": "kuznetsova@college.ru"},
    ]
    
    print("👥 Добавляем тестовых студентов...")
    
    for student in sample_students:
        success = add_user(
            username=student["username"],
            password=student["password"],
            role="Студент",
            full_name=student["full_name"],
            group_name=student["group"],
            email=student["email"]
        )
        if success:
            print(f"   ✅ {student['full_name']} ({student['username']})")
        else:
            print(f"   ❌ {student['full_name']} - уже существует")
    
    print("✅ Тестовые студенты добавлены!")

if __name__ == "__main__":
    print("=" * 60)
    print("🎓 DB Learn - Генератор тестовых данных")
    print("=" * 60)
    
    # Добавляем студентов
    add_sample_students()
    print()
    
    # Добавляем тесты
    add_sample_tests()
    
    print("\n🎉 Генерация завершена! Запустите приложение и проверьте данные.")
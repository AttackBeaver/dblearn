import sqlite3
import bcrypt
import os
import hashlib
import json
from typing import Optional, List, Dict, Any

DB_PATH = "data/users.db"


class DatabaseManager:
    """Менеджер для работы с базой данных"""
    
    @staticmethod
    def get_connection():
        """Создает и возвращает соединение с БД"""
        os.makedirs("data", exist_ok=True)
        return sqlite3.connect(DB_PATH)


def init_db():
    """Инициализация базы данных и создание таблиц"""
    conn = DatabaseManager.get_connection()
    c = conn.cursor()

    # Таблица пользователей
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        username TEXT PRIMARY KEY,
        password TEXT NOT NULL,
        role TEXT NOT NULL,
        full_name TEXT,
        group_name TEXT,
        email TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')

    # Таблица тестов
    c.execute('''CREATE TABLE IF NOT EXISTS tests (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        description TEXT,
        time_limit INTEGER DEFAULT 60,
        max_attempts INTEGER DEFAULT 1,
        shuffle_questions BOOLEAN DEFAULT TRUE,
        show_results BOOLEAN DEFAULT FALSE,
        created_by TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        is_active BOOLEAN DEFAULT TRUE
    )''')

    # Таблица вопросов
    c.execute('''CREATE TABLE IF NOT EXISTS test_questions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        test_id INTEGER,
        question_text TEXT NOT NULL,
        question_type TEXT DEFAULT 'single_choice',
        options JSON,
        points INTEGER DEFAULT 1,
        question_order INTEGER,
        FOREIGN KEY (test_id) REFERENCES tests (id) ON DELETE CASCADE
    )''')

    # Таблица правильных ответов
    c.execute('''CREATE TABLE IF NOT EXISTS test_answers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        question_id INTEGER,
        correct_answers JSON NOT NULL,
        answer_hash TEXT NOT NULL,
        FOREIGN KEY (question_id) REFERENCES test_questions (id) ON DELETE CASCADE
    )''')

    # Таблица результатов
    c.execute('''CREATE TABLE IF NOT EXISTS test_results (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        test_id INTEGER,
        student_username TEXT,
        answers JSON,
        score INTEGER,
        max_score INTEGER,
        time_spent INTEGER,
        completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        attempt_number INTEGER,
        FOREIGN KEY (test_id) REFERENCES tests (id),
        FOREIGN KEY (student_username) REFERENCES users (username)
    )''')

    conn.commit()
    conn.close()

    create_default_teacher()


def create_default_teacher():
    """Создает преподавателя по умолчанию"""
    conn = DatabaseManager.get_connection()
    c = conn.cursor()

    c.execute("SELECT username FROM users WHERE username = ?", ("teacher",))
    if not c.fetchone():
        hashed_password = bcrypt.hashpw("10209065".encode('utf-8'), bcrypt.gensalt())
        
        c.execute("""INSERT INTO users (username, password, role, full_name, group_name, email) 
                     VALUES (?, ?, ?, ?, ?, ?)""",
                  ("teacher", hashed_password, "Преподаватель", "Преподаватель", "ИТ-преподаватели", "teacher@college.ru"))
        conn.commit()
        print("✅ Преподаватель teacher создан")
    
    conn.close()


# =============================================================================
# ФУНКЦИИ ДЛЯ РАБОТЫ С ПОЛЬЗОВАТЕЛЯМИ
# =============================================================================

def add_user(username: str, password: str, role: str, full_name: Optional[str] = None, 
             group_name: Optional[str] = None, email: Optional[str] = None) -> bool:
    """Добавление нового пользователя"""
    conn = DatabaseManager.get_connection()
    c = conn.cursor()

    # Проверка существующего пользователя
    c.execute("SELECT username FROM users WHERE username = ?", (username,))
    if c.fetchone():
        conn.close()
        return False

    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    c.execute("""INSERT INTO users (username, password, role, full_name, group_name, email) 
                 VALUES (?, ?, ?, ?, ?, ?)""",
              (username, hashed_password, role, full_name, group_name, email))
    
    conn.commit()
    conn.close()
    return True


def authenticate_user(username: str, password: str) -> bool:
    """Аутентификация пользователя"""
    conn = DatabaseManager.get_connection()
    c = conn.cursor()
    
    c.execute("SELECT password FROM users WHERE username = ?", (username,))
    result = c.fetchone()
    conn.close()
    
    if result and bcrypt.checkpw(password.encode('utf-8'), result[0]):
        return True
    return False


def get_user_role(username: str) -> Optional[str]:
    """Получение роли пользователя"""
    conn = DatabaseManager.get_connection()
    c = conn.cursor()
    
    c.execute("SELECT role FROM users WHERE username = ?", (username,))
    result = c.fetchone()
    conn.close()
    
    return result[0] if result else None


def get_all_students() -> List[Dict[str, Any]]:
    """Получение списка всех студентов"""
    conn = DatabaseManager.get_connection()
    c = conn.cursor()
    
    c.execute("SELECT username, full_name, group_name, email FROM users WHERE role = 'Студент'")
    students = [
        {
            "username": row[0],
            "full_name": row[1],
            "group": row[2],
            "email": row[3]
        } for row in c.fetchall()
    ]
    
    conn.close()
    return students


def get_student_data(username: str) -> Optional[Dict[str, Any]]:
    """Получение данных студента"""
    conn = DatabaseManager.get_connection()
    c = conn.cursor()
    
    c.execute("SELECT username, full_name, group_name, email, created_at FROM users WHERE username = ?", (username,))
    result = c.fetchone()
    conn.close()

    if result:
        return {
            "username": result[0],
            "full_name": result[1],
            "group": result[2],
            "email": result[3],
            "created_at": result[4]
        }
    return None


# =============================================================================
# ФУНКЦИИ ДЛЯ СИСТЕМЫ ТЕСТИРОВАНИЯ
# =============================================================================

def hash_answer(answer: Any) -> str:
    """Хеширование ответа с солью"""
    if isinstance(answer, list):
        answer_str = json.dumps(sorted(answer), ensure_ascii=False)
    else:
        answer_str = str(answer).strip().lower()

    salt = "dblearn_secure_salt_2024"
    return hashlib.sha256(f"{answer_str}{salt}".encode()).hexdigest()


def create_test(title: str, description: str, time_limit: int = 60, 
                max_attempts: int = 1, created_by: str = "teacher") -> int:
    """Создание нового теста"""
    conn = DatabaseManager.get_connection()
    c = conn.cursor()
    
    c.execute("""INSERT INTO tests (title, description, time_limit, max_attempts, created_by) 
                 VALUES (?, ?, ?, ?, ?)""",
              (title, description, time_limit, max_attempts, created_by))
    
    test_id = c.lastrowid
    conn.commit()
    conn.close()
    
    return test_id


def create_secure_question(test_id: int, question_text: str, options: List[str], 
                          correct_answers: List[str], question_type: str = "single_choice", 
                          points: int = 1, question_order: int = 0) -> int:
    """Создание вопроса с хешированными ответами"""
    conn = DatabaseManager.get_connection()
    c = conn.cursor()

    # Сохраняем вопрос
    c.execute("""INSERT INTO test_questions (test_id, question_text, question_type, options, points, question_order) 
                 VALUES (?, ?, ?, ?, ?, ?)""",
              (test_id, question_text, question_type, json.dumps(options), points, question_order))

    question_id = c.lastrowid

    # Сохраняем хеши правильных ответов
    answers_hash = hash_answer(correct_answers)
    c.execute("""INSERT INTO test_answers (question_id, correct_answers, answer_hash) 
                 VALUES (?, ?, ?)""",
              (question_id, json.dumps(correct_answers), answers_hash))

    conn.commit()
    conn.close()
    
    return question_id


def verify_answer(question_id: int, student_answer: Any) -> bool:
    """Проверка ответа студента"""
    conn = DatabaseManager.get_connection()
    c = conn.cursor()

    c.execute("SELECT answer_hash FROM test_answers WHERE question_id = ?", (question_id,))
    result = c.fetchone()
    conn.close()

    if not result:
        return False

    return result[0] == hash_answer(student_answer)


def get_teacher_tests(username: str) -> List[Dict[str, Any]]:
    """Получение тестов преподавателя"""
    conn = DatabaseManager.get_connection()
    c = conn.cursor()
    
    c.execute("SELECT * FROM tests WHERE created_by = ? ORDER BY created_at DESC", (username,))
    
    tests = []
    for row in c.fetchall():
        tests.append({
            'id': row[0],
            'title': row[1],
            'description': row[2],
            'time_limit': row[3],
            'max_attempts': row[4],
            'shuffle_questions': bool(row[5]),
            'show_results': bool(row[6]),
            'created_by': row[7],
            'created_at': row[8],
            'is_active': bool(row[9])
        })

    conn.close()
    return tests


def get_test_questions(test_id: int) -> List[Dict[str, Any]]:
    """Получение вопросов теста"""
    conn = DatabaseManager.get_connection()
    c = conn.cursor()
    
    c.execute("SELECT * FROM test_questions WHERE test_id = ? ORDER BY question_order", (test_id,))
    
    questions = []
    for row in c.fetchall():
        questions.append({
            'id': row[0],
            'test_id': row[1],
            'question_text': row[2],
            'question_type': row[3],
            'options': json.loads(row[4]) if row[4] else [],
            'points': row[5],
            'question_order': row[6]
        })

    conn.close()
    return questions


def get_available_tests(student_username: str) -> List[Dict[str, Any]]:
    """Получение доступных тестов для студента"""
    conn = DatabaseManager.get_connection()
    c = conn.cursor()

    c.execute("""SELECT t.*, 
                COALESCE(MAX(r.attempt_number), 0) as current_attempt,
                COUNT(r.id) as completed_count
                FROM tests t
                LEFT JOIN test_results r ON t.id = r.test_id AND r.student_username = ?
                WHERE t.is_active = TRUE
                GROUP BY t.id
                HAVING completed_count < t.max_attempts OR t.max_attempts = 0
                """, (student_username,))

    tests = []
    for row in c.fetchall():
        tests.append({
            'id': row[0],
            'title': row[1],
            'description': row[2],
            'time_limit': row[3],
            'max_attempts': row[4],
            'shuffle_questions': bool(row[5]),
            'show_results': bool(row[6]),
            'current_attempt': row[10] + 1,
            'completed_count': row[11]
        })

    conn.close()
    return tests


def submit_test_answers(test_id: int, student_username: str, 
                       answers: Dict[str, Any], time_spent: int) -> tuple[int, int]:
    """Отправка ответов на тест"""
    conn = DatabaseManager.get_connection()
    c = conn.cursor()

    questions = get_test_questions(test_id)
    max_score = sum(q['points'] for q in questions)
    score = 0

    # Проверяем ответы и считаем баллы
    for question in questions:
        student_answer = answers.get(str(question['id']))
        if student_answer and verify_answer(question['id'], student_answer):
            score += question['points']

    # Определяем номер попытки
    c.execute("""SELECT COALESCE(MAX(attempt_number), 0) 
                 FROM test_results 
                 WHERE test_id = ? AND student_username = ?""",
              (test_id, student_username))
    attempt_number = c.fetchone()[0] + 1

    # Сохраняем результат
    c.execute("""INSERT INTO test_results (test_id, student_username, answers, score, max_score, time_spent, attempt_number)
                 VALUES (?, ?, ?, ?, ?, ?, ?)""",
              (test_id, student_username, json.dumps(answers), score, max_score, time_spent, attempt_number))

    conn.commit()
    conn.close()
    
    return score, max_score


def get_test_results(student_username: str, test_id: Optional[int] = None) -> List[Dict[str, Any]]:
    """Получение результатов тестов"""
    conn = DatabaseManager.get_connection()
    c = conn.cursor()

    if test_id:
        c.execute("""SELECT r.*, t.title 
                     FROM test_results r 
                     JOIN tests t ON r.test_id = t.id 
                     WHERE r.student_username = ? AND r.test_id = ?
                     ORDER BY r.completed_at DESC""",
                  (student_username, test_id))
    else:
        c.execute("""SELECT r.*, t.title 
                     FROM test_results r 
                     JOIN tests t ON r.test_id = t.id 
                     WHERE r.student_username = ? 
                     ORDER BY r.completed_at DESC""",
                  (student_username,))

    results = []
    for row in c.fetchall():
        results.append({
            'id': row[0],
            'test_id': row[1],
            'test_title': row[9],
            'score': row[4],
            'max_score': row[5],
            'time_spent': row[6],
            'completed_at': row[7],
            'attempt_number': row[8]
        })

    conn.close()
    return results


def get_test_by_id(test_id: int) -> Optional[Dict[str, Any]]:
    """Получение теста по ID"""
    conn = DatabaseManager.get_connection()
    c = conn.cursor()
    
    c.execute("SELECT * FROM tests WHERE id = ?", (test_id,))
    row = c.fetchone()
    conn.close()

    if row:
        return {
            'id': row[0],
            'title': row[1],
            'description': row[2],
            'time_limit': row[3],
            'max_attempts': row[4],
            'shuffle_questions': bool(row[5]),
            'show_results': bool(row[6]),
            'created_by': row[7],
            'created_at': row[8],
            'is_active': bool(row[9])
        }
    return None


# =============================================================================
# ФУНКЦИИ АНАЛИТИКИ И СТАТИСТИКИ
# =============================================================================

def get_group_statistics(group_name: str) -> Optional[Dict[str, Any]]:
    """Статистика по группе"""
    try:
        conn = DatabaseManager.get_connection()
        c = conn.cursor()
        
        # Получаем студентов группы
        c.execute("SELECT username FROM users WHERE role = 'Студент' AND group_name = ?", (group_name,))
        students = [row[0] for row in c.fetchall()]
        
        if not students:
            conn.close()
            return None
        
        # Статистика по тестам
        placeholders = ','.join('?' for _ in students)
        c.execute(f"""
            SELECT 
                COUNT(DISTINCT test_id) as total_tests,
                COUNT(*) as total_attempts,
                AVG(score * 100.0 / max_score) as avg_success_rate,
                MAX(score * 100.0 / max_score) as max_success_rate,
                MIN(score * 100.0 / max_score) as min_success_rate
            FROM test_results 
            WHERE student_username IN ({placeholders})
        """, students)
        
        stats = c.fetchone()
        
        # Распределение оценок
        c.execute(f"""
            SELECT 
                CASE 
                    WHEN score * 100.0 / max_score >= 90 THEN '90-100%'
                    WHEN score * 100.0 / max_score >= 80 THEN '80-89%'
                    WHEN score * 100.0 / max_score >= 70 THEN '70-79%'
                    WHEN score * 100.0 / max_score >= 60 THEN '60-69%'
                    ELSE '0-59%'
                END as grade_range,
                COUNT(*) as count
            FROM test_results 
            WHERE student_username IN ({placeholders})
            GROUP BY grade_range
            ORDER BY grade_range
        """, students)
        
        grade_distribution = {row[0]: row[1] for row in c.fetchall()}
        
        conn.close()
        
        return {
            'group_name': group_name,
            'student_count': len(students),
            'total_tests': stats[0] or 0,
            'total_attempts': stats[1] or 0,
            'avg_success_rate': round(stats[2] or 0, 1),
            'max_success_rate': round(stats[3] or 0, 1),
            'min_success_rate': round(stats[4] or 0, 1),
            'grade_distribution': grade_distribution
        }
    except Exception as e:
        print(f"Ошибка в get_group_statistics: {e}")
        return None


def get_student_progress(student_username: str) -> List[Dict[str, Any]]:
    """Прогресс студента"""
    conn = DatabaseManager.get_connection()
    c = conn.cursor()
    
    c.execute("""
        SELECT 
            DATE(completed_at) as date,
            AVG(score * 100.0 / max_score) as daily_avg,
            COUNT(*) as tests_taken
        FROM test_results 
        WHERE student_username = ?
        GROUP BY DATE(completed_at)
        ORDER BY date
    """, (student_username,))
    
    progress_data = []
    for row in c.fetchall():
        progress_data.append({
            'date': row[0],
            'daily_avg': round(row[1], 1),
            'tests_taken': row[2]
        })
    
    conn.close()
    return progress_data


def get_test_analytics(test_id: int) -> Dict[str, Any]:
    """Аналитика по тесту"""
    conn = DatabaseManager.get_connection()
    c = conn.cursor()
    
    # Основная статистика
    c.execute("""
        SELECT 
            COUNT(*) as total_attempts,
            AVG(score) as avg_score,
            MAX(score) as max_score_achieved,
            MIN(score) as min_score_achieved,
            AVG(time_spent) as avg_time_spent,
            AVG(score * 100.0 / max_score) as avg_success_rate
        FROM test_results 
        WHERE test_id = ?
    """, (test_id,))
    
    stats = c.fetchone()
    
    # Информация о тесте
    c.execute("SELECT title, description FROM tests WHERE id = ?", (test_id,))
    test_info = c.fetchone()
    
    # Количество вопросов
    c.execute("SELECT COUNT(*) FROM test_questions WHERE test_id = ?", (test_id,))
    question_count = c.fetchone()[0]
    
    # Распределение оценок
    c.execute("""
        SELECT 
            CASE 
                WHEN score * 100.0 / max_score >= 90 THEN '90-100%'
                WHEN score * 100.0 / max_score >= 80 THEN '80-89%'
                WHEN score * 100.0 / max_score >= 70 THEN '70-79%'
                WHEN score * 100.0 / max_score >= 60 THEN '60-69%'
                ELSE '0-59%'
            END as grade_range,
            COUNT(*) as count
        FROM test_results 
        WHERE test_id = ?
        GROUP BY grade_range
        ORDER BY grade_range
    """, (test_id,))
    
    grade_distribution = {row[0]: row[1] for row in c.fetchall()}
    
    conn.close()
    
    return {
        'test_id': test_id,
        'title': test_info[0] if test_info else "Неизвестный тест",
        'description': test_info[1] if test_info else "",
        'question_count': question_count,
        'total_attempts': stats[0] or 0,
        'avg_score': round(stats[1] or 0, 1),
        'max_score_achieved': stats[2] or 0,
        'min_score_achieved': stats[3] or 0,
        'avg_time_spent': round(stats[4] or 0, 1),
        'avg_success_rate': round(stats[5] or 0, 1),
        'grade_distribution': grade_distribution
    }


def get_student_ranking() -> List[Dict[str, Any]]:
    """Рейтинг студентов"""
    conn = DatabaseManager.get_connection()
    c = conn.cursor()
    
    c.execute("""
        SELECT 
            u.username,
            u.full_name,
            u.group_name,
            COUNT(r.id) as tests_completed,
            AVG(r.score * 100.0 / r.max_score) as avg_success_rate,
            SUM(r.score) as total_points
        FROM users u
        LEFT JOIN test_results r ON u.username = r.student_username
        WHERE u.role = 'Студент'
        GROUP BY u.username
        HAVING tests_completed > 0
        ORDER BY avg_success_rate DESC
        LIMIT 20
    """)
    
    ranking = []
    for i, row in enumerate(c.fetchall(), 1):
        ranking.append({
            'rank': i,
            'username': row[0],
            'full_name': row[1],
            'group': row[2],
            'tests_completed': row[3],
            'avg_success_rate': round(row[4] or 0, 1),
            'total_points': row[5] or 0
        })
    
    conn.close()
    return ranking


def get_teacher_dashboard_stats(teacher_username: str) -> Dict[str, Any]:
    """Статистика для дашборда преподавателя"""
    try:
        conn = DatabaseManager.get_connection()
        c = conn.cursor()
        
        c.execute("""
            SELECT 
                COUNT(DISTINCT id) as total_tests,
                (SELECT COUNT(DISTINCT username) FROM users WHERE role = 'Студент') as total_students,
                (SELECT COUNT(DISTINCT group_name) FROM users WHERE role = 'Студент' AND group_name IS NOT NULL) as total_groups
            FROM tests 
            WHERE created_by = ?
        """, (teacher_username,))
        
        metrics = c.fetchone()
        conn.close()
        
        return {
            'total_tests': metrics[0] or 0,
            'total_students': metrics[1] or 0,
            'total_groups': metrics[2] or 0
        }
    except Exception as e:
        print(f"Ошибка в get_teacher_dashboard_stats: {e}")
        return {
            'total_tests': 0,
            'total_students': 0,
            'total_groups': 0
        }
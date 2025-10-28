import json
from pathlib import Path

TESTS_PATH = Path("data/tests")


def get_available_tests():
    """
    Возвращает список доступных тестов по именам файлов.
    Пример: ['select', 'join', 'groupby']
    """
    TESTS_PATH.mkdir(parents=True, exist_ok=True)
    return [f.stem for f in TESTS_PATH.glob("*.json")]


def load_test(test_name: str):
    """
    Загружает тест по имени файла (без расширения).
    Возвращает словарь с темой и списком вопросов.
    Пример структуры:
    {
      "topic": "SELECT",
      "questions": [
        {
          "question": "Что делает оператор SELECT?",
          "options": ["Создает таблицу", "Выбирает данные", "Удаляет строку"],
          "answer": 1
        }
      ]
    }
    """
    file_path = TESTS_PATH / f"{test_name}.json"
    if not file_path.exists():
        raise FileNotFoundError(f"Тест '{test_name}' не найден")
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data


def validate_test_structure(data: dict) -> bool:
    """
    Проверяет корректность структуры JSON.
    """
    if "topic" not in data or "questions" not in data:
        return False
    for q in data["questions"]:
        if not all(k in q for k in ["question", "options", "answer"]):
            return False
    return True

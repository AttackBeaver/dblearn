# DB Learn

``` txt
dblearn/
│
├── app.py                         # Главный файл Streamlit-приложения
│
├── requirements.txt               # Зависимости (streamlit, pandas, sqlite3 и др.)
│
├── data/
│   ├── users.db                   # SQLite-база для хранения пользователей и результатов
│   └── tests/
│       └── test-1.json           # Тест 1
│
├── modules/
│   ├── auth.py                    # Авторизация и регистрация
│   ├── test_loader.py             # Загрузка JSON-тестов
│   ├── quiz_engine.py             # Логика тестирования и подсчёта баллов
│   ├── results.py                 # Запись и отображение результатов
│   └── db_init.py                 # Создание БД и таблиц при первом запуске
│
├── assets/
│   ├── logo.png                   # Логотип приложения
│   └── style.css                  # Кастомное оформление (при необходимости)
│
└── README.md                      # Краткое описание и инструкция по запуску
```

## Запуск проекта

1. Клонировать репозиторий или скачать проект.
2. Создать и активировать виртуальное окружение:

   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```

3. Установить зависимости:

   ```bash
   pip install -r requirements.txt
   ```

4. Запустить Streamlit-приложение:

   ```bash
   streamlit run src/app.py
   ```

После запуска в терминале появится ссылка, например:

``` txt
Local URL: http://localhost:8501
```

Открой её в браузере.

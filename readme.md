# DB Learn

## Ссылка доступа: <https://dblearn-spk.streamlit.app/>

``` txt
db_security_app/
│
├── app.py                     # Главный файл Streamlit
├── database/
│   ├── __init__.py
│   └── db_manager.py          # Подключение и операции с БД
│
├── auth/
│   ├── __init__.py
│   └── auth_manager.py        # Регистрация, вход, проверка ролей
│
├── data/
│   └── users.db               # SQLite база пользователей
│
├── tests/
│   └── test_auth.py
│
├── requirements.txt
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
   streamlit run app.py
   ```

После запуска в терминале появится ссылка, например:

``` txt
Local URL: http://localhost:8501
```

Открой её в браузере.

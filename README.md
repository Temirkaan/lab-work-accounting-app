# Система учёта выполненных лабораторных работ

Flask-приложение для контроля сдачи, проверки и доработки лабораторных работ студентов.

## Что где находится

### Техническое задание

- `docs/zadanie_1_tz.docx` - ТЗ по заданию 1.

### Серверная часть

- `app.py` - Flask-маршруты для студентов, лабораторных, сдач и API.
- `database.py` - Функции SQLite, создание таблиц, демо-данные и обновление статусов.

### Клиентская часть

- `templates/index.html` - HTML-шаблон интерфейса учёта лабораторных.
- `static/styles.css` - Стили форм, карточек, статистики и кнопок.

### База данных

- `lab_works.db` - SQLite-база с демо-данными.
- `schema.sql` - SQL-схема таблиц students, lab_works, submissions.
- `database.py` - SQL-запросы приложения.

## Отдельные отчёты по заданиям

- `docs/zadanie_2_server.docx` - серверная часть.
- `docs/zadanie_3_client.docx` - клиентская часть.
- `docs/zadanie_4_database.docx` - база данных.

## Запуск

```powershell
pip install -r requirements.txt
python app.py
```

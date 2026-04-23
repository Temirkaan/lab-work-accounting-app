import sqlite3
from pathlib import Path


DB_PATH = Path(__file__).with_name("lab_works.db")
SCHEMA_SQL = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name TEXT NOT NULL,
    group_name TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS lab_works (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    subject TEXT NOT NULL,
    max_score INTEGER NOT NULL DEFAULT 5,
    deadline TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS submissions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    lab_work_id INTEGER NOT NULL,
    submitted_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    score INTEGER,
    status TEXT NOT NULL DEFAULT 'submitted'
        CHECK (status IN ('submitted', 'checked', 'revision')),
    comment TEXT,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
    FOREIGN KEY (lab_work_id) REFERENCES lab_works(id) ON DELETE CASCADE
);
"""


def get_connection():
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def init_db():
    with get_connection() as connection:
        connection.executescript(SCHEMA_SQL)


def seed_demo_data():
    with get_connection() as connection:
        count = connection.execute("SELECT COUNT(*) FROM students").fetchone()[0]
        if count:
            return
        connection.executemany(
            "INSERT INTO students (full_name, group_name) VALUES (?, ?)",
            [
                ("Алексеева Мария", "ИС-21"),
                ("Иванов Никита", "ИС-21"),
                ("Петрова Анна", "ИС-22"),
            ],
        )
        connection.executemany(
            "INSERT INTO lab_works (title, subject, max_score, deadline) VALUES (?, ?, ?, ?)",
            [
                ("Лабораторная работа №1", "Базы данных", 5, "2026-04-26"),
                ("Лабораторная работа №2", "Веб-разработка", 5, "2026-05-03"),
                ("Лабораторная работа №3", "Тестирование ПО", 5, "2026-05-10"),
            ],
        )
        connection.executemany(
            """
            INSERT INTO submissions (student_id, lab_work_id, score, status, comment)
            VALUES (
                (SELECT id FROM students WHERE full_name = ?),
                (SELECT id FROM lab_works WHERE title = ?),
                ?, ?, ?
            )
            """,
            [
                ("Алексеева Мария", "Лабораторная работа №1", 5, "checked", "Работа принята"),
                ("Иванов Никита", "Лабораторная работа №1", None, "submitted", "Ожидает проверки"),
                ("Петрова Анна", "Лабораторная работа №2", 3, "revision", "Нужно исправить вывод"),
            ],
        )


def get_stats():
    with get_connection() as connection:
        students = connection.execute("SELECT COUNT(*) FROM students").fetchone()[0]
        labs = connection.execute("SELECT COUNT(*) FROM lab_works").fetchone()[0]
        submitted = connection.execute("SELECT COUNT(*) FROM submissions WHERE status = 'submitted'").fetchone()[0]
        checked = connection.execute("SELECT COUNT(*) FROM submissions WHERE status = 'checked'").fetchone()[0]
        return {"students": students, "labs": labs, "submitted": submitted, "checked": checked}


def get_students():
    with get_connection() as connection:
        rows = connection.execute("SELECT * FROM students ORDER BY group_name, full_name").fetchall()
        return [dict(row) for row in rows]


def get_labs():
    with get_connection() as connection:
        rows = connection.execute("SELECT * FROM lab_works ORDER BY deadline").fetchall()
        return [dict(row) for row in rows]


def add_student(full_name, group_name):
    with get_connection() as connection:
        cursor = connection.execute("INSERT INTO students (full_name, group_name) VALUES (?, ?)", (full_name, group_name))
        return cursor.lastrowid


def add_lab(title, subject, max_score, deadline):
    with get_connection() as connection:
        cursor = connection.execute(
            "INSERT INTO lab_works (title, subject, max_score, deadline) VALUES (?, ?, ?, ?)",
            (title, subject, max_score, deadline),
        )
        return cursor.lastrowid


def get_submissions(status=None, group_name=None):
    query = """
        SELECT
            submissions.*,
            students.full_name,
            students.group_name,
            lab_works.title,
            lab_works.subject,
            lab_works.deadline
        FROM submissions
        JOIN students ON students.id = submissions.student_id
        JOIN lab_works ON lab_works.id = submissions.lab_work_id
    """
    conditions = []
    params = []
    if status:
        conditions.append("submissions.status = ?")
        params.append(status)
    if group_name:
        conditions.append("students.group_name LIKE ?")
        params.append(f"%{group_name}%")
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    query += " ORDER BY submissions.submitted_at DESC, submissions.id DESC"
    with get_connection() as connection:
        rows = connection.execute(query, params).fetchall()
        return [dict(row) for row in rows]


def add_submission(student_id, lab_work_id, comment):
    with get_connection() as connection:
        cursor = connection.execute(
            "INSERT INTO submissions (student_id, lab_work_id, comment) VALUES (?, ?, ?)",
            (student_id, lab_work_id, comment),
        )
        return cursor.lastrowid


def check_submission(submission_id, score, comment):
    with get_connection() as connection:
        connection.execute(
            "UPDATE submissions SET status = 'checked', score = ?, comment = ? WHERE id = ?",
            (score, comment, submission_id),
        )


def request_revision(submission_id, comment):
    with get_connection() as connection:
        connection.execute(
            "UPDATE submissions SET status = 'revision', comment = ? WHERE id = ?",
            (comment, submission_id),
        )

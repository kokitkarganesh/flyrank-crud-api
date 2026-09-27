import os
import time

import psycopg
from dotenv import load_dotenv


load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not set")


def get_connection():
    return psycopg.connect(DATABASE_URL)


def init_database():
    last_error = None

    for _ in range(10):
        try:
            with get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        CREATE TABLE IF NOT EXISTS tasks (
                            id SERIAL PRIMARY KEY,
                            title TEXT NOT NULL,
                            done BOOLEAN NOT NULL DEFAULT FALSE
                        )
                        """
                    )

                    cur.execute("SELECT COUNT(*) FROM tasks")
                    count = cur.fetchone()[0]

                    if count == 0:
                        cur.executemany(
                            "INSERT INTO tasks (title, done) VALUES (%s, %s)",
                            [
                                ("Learn FastAPI", False),
                                ("Connect PostgreSQL", False),
                                ("Build CRUD API", False),
                            ],
                        )

                conn.commit()

            return

        except psycopg.OperationalError as error:
            last_error = error
            time.sleep(2)

    raise RuntimeError(
        f"Could not connect to PostgreSQL: {last_error}"
    )


def get_all_tasks():
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT id, title, done FROM tasks ORDER BY id"
            )
            rows = cursor.fetchall()

    return [
        {
            "id": row[0],
            "title": row[1],
            "done": row[2],
        }
        for row in rows
    ]


def get_task_by_id(task_id: int):
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT id, title, done FROM tasks WHERE id = %s",
                (task_id,),
            )
            row = cursor.fetchone()

    if row is None:
        return None

    return {
        "id": row[0],
        "title": row[1],
        "done": row[2],
    }
from pathlib import Path
import os
import sqlite3

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel


BASE_DIR = Path(__file__).resolve().parent
DB_PATH = Path(os.getenv("TASKS_DB_PATH", str(BASE_DIR / "tasks.db")))

app = FastAPI(
    title="Task API",
    version="2.0",
    description="A small FastAPI CRUD API backed by a persistent SQLite database.",
)


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": str(exc.detail)},
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=400,
        content={"error": "Invalid request body"},
    )


class TaskCreate(BaseModel):
    title: str
    done: bool | None = None


class TaskUpdate(BaseModel):
    title: str | None = None
    done: bool | None = None


def get_connection() -> sqlite3.Connection:
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def init_database() -> None:
    with get_connection() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                done INTEGER NOT NULL DEFAULT 0
            )
            """
        )

        count = connection.execute(
            "SELECT COUNT(*) FROM tasks"
        ).fetchone()[0]

        if count == 0:
            seed_tasks = [
                ("Learn FastAPI", 0),
                ("Build CRUD API", 0),
                ("Test with Swagger", 0),
            ]
            connection.executemany(
                "INSERT INTO tasks (title, done) VALUES (?, ?)",
                seed_tasks,
            )


def row_to_task(row: sqlite3.Row) -> dict:
    return {
        "id": row["id"],
        "title": row["title"],
        "done": bool(row["done"]),
    }


def get_task_by_id(task_id: int) -> dict | None:
    with get_connection() as connection:
        row = connection.execute(
            "SELECT * FROM tasks WHERE id = ?",
            (task_id,),
        ).fetchone()

    return row_to_task(row) if row else None


init_database()


@app.get("/", summary="API information")
def root():
    return {
        "name": "Task API",
        "version": "2.0",
        "endpoints": ["/tasks"],
    }


@app.get("/health", summary="Health check")
def health():
    return {"status": "ok"}


@app.get("/tasks", summary="List all tasks")
def list_tasks():
    with get_connection() as connection:
        rows = connection.execute(
            "SELECT * FROM tasks ORDER BY id"
        ).fetchall()

    return [row_to_task(row) for row in rows]


@app.get("/tasks/{task_id}", summary="Get one task")
def get_task(task_id: int):
    task = get_task_by_id(task_id)

    if task is None:
        raise HTTPException(
            status_code=404,
            detail=f"Task {task_id} not found",
        )

    return task


@app.post("/tasks", status_code=201, summary="Create a task")
def create_task(task: TaskCreate):
    title = task.title.strip()

    if not title:
        raise HTTPException(
            status_code=400,
            detail="Title must not be empty",
        )

    with get_connection() as connection:
        cursor = connection.execute(
            "INSERT INTO tasks (title, done) VALUES (?, ?)",
            (title, 0),
        )
        task_id = cursor.lastrowid

    return {
        "id": task_id,
        "title": title,
        "done": False,
    }


@app.put("/tasks/{task_id}", summary="Update a task")
def update_task(task_id: int, task: TaskUpdate):
    if task.title is None and task.done is None:
        raise HTTPException(
            status_code=400,
            detail="Request body must include title or done",
        )

    existing = get_task_by_id(task_id)

    if existing is None:
        raise HTTPException(
            status_code=404,
            detail=f"Task {task_id} not found",
        )

    new_title = existing["title"]
    new_done = existing["done"]

    if task.title is not None:
        new_title = task.title.strip()

        if not new_title:
            raise HTTPException(
                status_code=400,
                detail="Title must not be empty",
            )

    if task.done is not None:
        new_done = task.done

    with get_connection() as connection:
        connection.execute(
            """
            UPDATE tasks
            SET title = ?, done = ?
            WHERE id = ?
            """,
            (new_title, int(new_done), task_id),
        )

    return {
        "id": task_id,
        "title": new_title,
        "done": new_done,
    }


@app.delete("/tasks/{task_id}", status_code=204, summary="Delete a task")
def delete_task(task_id: int):
    with get_connection() as connection:
        cursor = connection.execute(
            "DELETE FROM tasks WHERE id = ?",
            (task_id,),
        )

        if cursor.rowcount == 0:
            raise HTTPException(
                status_code=404,
                detail=f"Task {task_id} not found",
            )

    return None

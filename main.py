from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from repository import (
    create_task,
    delete_task as delete_task_from_db,
    get_all_tasks,
    get_task_by_id,
    init_database,
    update_task as update_task_in_db,
)


app = FastAPI(
    title="Task API",
    version="3.0",
    description="A small FastAPI CRUD API backed by PostgreSQL.",
)


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": str(exc.detail)},
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
):
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


init_database()


@app.get("/")
def root():
    return {
        "name": "Task API",
        "version": "3.0",
        "endpoints": ["/tasks"],
    }


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/tasks")
def list_tasks():
    return get_all_tasks()


@app.get("/tasks/{task_id}")
def get_task(task_id: int):
    task = get_task_by_id(task_id)

    if task is None:
        raise HTTPException(404, "Task not found")

    return task


@app.post("/tasks", status_code=201)
def create_new_task(task: TaskCreate):
    title = task.title.strip()

    if not title:
        raise HTTPException(400, "Title must not be empty")

    done = task.done if task.done is not None else False

    return create_task(title, done)


@app.put("/tasks/{task_id}")
def update_existing_task(task_id: int, task: TaskUpdate):
    if task.title is None and task.done is None:
        raise HTTPException(
            400,
            "Request body must include title or done",
        )

    existing = get_task_by_id(task_id)

    if existing is None:
        raise HTTPException(404, "Task not found")

    title = existing["title"]
    done = existing["done"]

    if task.title is not None:
        title = task.title.strip()

        if not title:
            raise HTTPException(400, "Title must not be empty")

    if task.done is not None:
        done = task.done

    return update_task_in_db(task_id, title, done)


@app.delete("/tasks/{task_id}", status_code=204)
def delete_existing_task(task_id: int):
    deleted = delete_task_from_db(task_id)

    if not deleted:
        raise HTTPException(404, "Task not found")

    return None
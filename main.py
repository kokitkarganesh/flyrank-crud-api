from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel

app = FastAPI(
    title="Task API",
    version="1.0",
    description="A small in-memory CRUD API for managing tasks.",
)


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(status_code=exc.status_code, content={"error": str(exc.detail)})


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(status_code=400, content={"error": "Invalid request body"})


class TaskCreate(BaseModel):
    title: str
    done: bool | None = None


class TaskUpdate(BaseModel):
    title: str | None = None
    done: bool | None = None


# In-memory storage: data is intentionally lost when the server restarts.
tasks = [
    {"id": 1, "title": "Learn FastAPI", "done": False},
    {"id": 2, "title": "Build CRUD API", "done": False},
    {"id": 3, "title": "Test with Swagger", "done": False},
]


def next_id() -> int:
    return max((task["id"] for task in tasks), default=0) + 1


@app.get("/", summary="API information")
def root():
    return {"name": "Task API", "version": "1.0", "endpoints": ["/tasks"]}


@app.get("/health", summary="Health check")
def health():
    return {"status": "ok"}


@app.get("/tasks", summary="List all tasks")
def list_tasks():
    return tasks


@app.get("/tasks/{task_id}", summary="Get one task")
def get_task(task_id: int):
    task = next((task for task in tasks if task["id"] == task_id), None)
    if task is None:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    return task


@app.post("/tasks", status_code=201, summary="Create a task")
def create_task(task: TaskCreate):
    title = task.title.strip()
    if not title:
        raise HTTPException(status_code=400, detail="Title must not be empty")

    new_task = {
        "id": next_id(),
        "title": title,
        "done": False,
    }
    tasks.append(new_task)
    return new_task


@app.put("/tasks/{task_id}", summary="Update a task")
def update_task(task_id: int, task: TaskUpdate):
    existing = next((task for task in tasks if task["id"] == task_id), None)
    if existing is None:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")

    if task.title is None and task.done is None:
        raise HTTPException(status_code=400, detail="Request body must include title or done")

    if task.title is not None:
        title = task.title.strip()
        if not title:
            raise HTTPException(status_code=400, detail="Title must not be empty")
        existing["title"] = title

    if task.done is not None:
        existing["done"] = task.done

    return existing


@app.delete("/tasks/{task_id}", status_code=204, summary="Delete a task")
def delete_task(task_id: int):
    index = next((i for i, task in enumerate(tasks) if task["id"] == task_id), None)
    if index is None:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")

    tasks.pop(index)
    return None

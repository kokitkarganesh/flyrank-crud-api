from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from repository import get_all_tasks, get_task_by_id, init_database


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


# Create the PostgreSQL table and seed the initial 3 tasks.
init_database()


@app.get("/", summary="API information")
def root():
    return {
        "name": "Task API",
        "version": "3.0",
        "endpoints": ["/tasks"],
    }


@app.get("/health", summary="Health check")
def health():
    return {"status": "ok"}


@app.get("/tasks", summary="List all tasks")
def list_tasks():
    return get_all_tasks()


@app.get("/tasks/{task_id}", summary="Get one task")
def get_task(task_id: int):
    task = get_task_by_id(task_id)

    if task is None:
        raise HTTPException(
            status_code=404,
            detail="Task not found",
        )

    return task


@app.post("/tasks", status_code=201, summary="Create a task")
def create_task(task: TaskCreate):
    # CRUD write operations will be added in Stage 3.
    raise HTTPException(
        status_code=501,
        detail="Create task will be implemented in Stage 3",
    )


@app.put("/tasks/{task_id}", summary="Update a task")
def update_task(task_id: int, task: TaskUpdate):
    # CRUD write operations will be added in Stage 3.
    raise HTTPException(
        status_code=501,
        detail="Update task will be implemented in Stage 3",
    )


@app.delete("/tasks/{task_id}", status_code=204, summary="Delete a task")
def delete_task(task_id: int):
    # CRUD write operations will be added in Stage 3.
    raise HTTPException(
        status_code=501,
        detail="Delete task will be implemented in Stage 3",
    )
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="Task API", version="1.0")

tasks = [
    {"id": 1, "title": "Learn FastAPI", "done": False},
    {"id": 2, "title": "Build CRUD API", "done": False},
    {"id": 3, "title": "Test with Swagger", "done": False},
]

class TaskCreate(BaseModel):
    title: str
    done: bool | None = None

def next_id() -> int:
    return max((task["id"] for task in tasks), default=0) + 1

@app.get("/")
def root():
    return {"name": "Task API", "version": "1.0", "endpoints": ["/tasks"]}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/tasks")
def list_tasks():
    return tasks

@app.get("/tasks/{task_id}")
def get_task(task_id: int):
    task = next((task for task in tasks if task["id"] == task_id), None)
    if task is None:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    return task

@app.post("/tasks", status_code=201)
def create_task(task: TaskCreate):
    title = task.title.strip()
    if not title:
        raise HTTPException(status_code=400, detail="Title must not be empty")
    new_task = {"id": next_id(), "title": title, "done": False}
    tasks.append(new_task)
    return new_task


class TaskUpdate(BaseModel):
    title: str | None = None
    done: bool | None = None

@app.put("/tasks/{task_id}")
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

@app.delete("/tasks/{task_id}", status_code=204)
def delete_task(task_id: int):
    index = next((i for i, task in enumerate(tasks) if task["id"] == task_id), None)
    if index is None:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    tasks.pop(index)
    return None

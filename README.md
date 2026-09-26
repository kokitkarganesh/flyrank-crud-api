# Task API — FlyRank Week 2 Assignment A1

A small **FastAPI CRUD API** that manages a to-do list using an in-memory Python list. It implements the six required stages from the FlyRank Backend Track Week 2 assignment.

> **Important:** No database or files are used for task storage. Restarting the server resets the data to the three example tasks, as required by the assignment.

## Requirements

- Python 3.10+
- pip

## Install and run

Create and activate a virtual environment, then install dependencies:

```bash
python -m venv .venv
```

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn main:app --reload
```

macOS/Linux:

```bash
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

The API runs at `http://localhost:8000`.

## Swagger UI

Open:

`http://localhost:8000/docs`

FastAPI generates the interactive Swagger UI automatically. Use **Try it out** to run the complete CRUD cycle.

## Endpoints

| Method | Endpoint | Purpose | Success | Errors |
|---|---|---|---|---|
| GET | `/` | API information | 200 | — |
| GET | `/health` | Health check | 200 | — |
| GET | `/tasks` | List all tasks | 200 | — |
| GET | `/tasks/{id}` | Get one task | 200 | 404 |
| POST | `/tasks` | Create task | 201 | 400 |
| PUT | `/tasks/{id}` | Update task | 200 | 400, 404 |
| DELETE | `/tasks/{id}` | Delete task | 204 | 404 |

## Example curl commands

### Read all tasks

```bash
curl -i http://localhost:8000/tasks
```

Expected status:

```text
HTTP/1.1 200 OK
```

### Read one task

```bash
curl -i http://localhost:8000/tasks/1
```

### Read an unknown task

```bash
curl -i http://localhost:8000/tasks/99
```

Expected JSON error:

```json
{"detail":"Task 99 not found"}
```

### Create a task

```bash
curl -i -X POST http://localhost:8000/tasks -H "Content-Type: application/json" -d '{"title":"Buy milk"}'
```

Expected status: `201 Created`.

### Update a task

```bash
curl -i -X PUT http://localhost:8000/tasks/1 -H "Content-Type: application/json" -d '{"done":true}'
```

Expected status: `200 OK`.

### Delete a task

```bash
curl -i -X DELETE http://localhost:8000/tasks/1
```

Expected status: `204 No Content`.

## Validation

- POST with a missing title returns `400` with a JSON error.
- POST with an empty/whitespace-only title returns `400`.
- POST creates a task with the next free numeric ID and `done: false`.
- PUT must contain at least `title` or `done`.
- PUT with an empty/whitespace-only title returns `400`.
- Unknown task IDs return `404`.

## Automated tests

Run:

```bash
pytest -q
```

The tests cover the root and health endpoints, read operations, 404 handling, create validation, update, and delete.

## In-memory data experiment

The task list is stored only in Python memory. If tasks are created or updated and the server is restarted, those changes disappear and the three seed tasks return. This is intentional: the assignment asks for in-memory storage, and Week 3 introduces the database persistence problem.

## AI vs me — Stage 7 bonus

### My prompt

> Build a Python 3.10+ FastAPI application for a beginner backend assignment. Create an in-memory to-do task API with three initial tasks. Each task must have a numeric id, string title, and boolean done field. Implement GET `/`, GET `/health`, GET `/tasks`, GET `/tasks/{id}`, POST `/tasks`, PUT `/tasks/{id}`, and DELETE `/tasks/{id}`. GET reads should return 200, missing task IDs should return 404 with a JSON error message, POST should create the next numeric ID, set done to false, and return 201, POST should reject missing or empty titles, PUT should update title and/or done and reject an empty body, and DELETE should return 204 with no body. Keep all data in memory and do not add a database or file storage. Add useful endpoint descriptions so FastAPI's Swagger UI at `/docs` documents the API. Keep the implementation simple enough for a beginner to understand.

### AI version

A separate generated version is stored in `ai-version/main.py` so the hand-built `main.py` remains untouched.

### Three differences to review

1. **Validation behavior:** FastAPI/Pydantic handles a missing `title` at the schema level, producing a framework-level `422` response, while an explicitly empty title is handled by our application and returns `400`.
2. **Update model:** The hand-built version uses a separate update model so `title` and `done` can each be updated independently, while an AI implementation may choose a different model or make fields required.
3. **ID generation:** The hand-built version calculates the next free ID from the current in-memory list instead of maintaining a separate counter, so deleting a task does not require synchronizing another variable.

### What the prompt could have specified better

The prompt could explicitly require the exact JSON error shape from the assignment (`{"error":"..."}` rather than FastAPI's default `{"detail":"..."}`) and could specify whether missing JSON fields should be `400` or framework validation errors. This project converts FastAPI request-validation failures into the assignment-required `400` JSON error response.

### Rematch change

For a second generation, the prompt should explicitly define the required error response shape and validation status codes to reduce ambiguity.

## Assignment checklist

- [x] Stage 0 — Hello server
- [x] Stage 1 — Root and health endpoints
- [x] Stage 2 — Read endpoints + 404
- [x] Stage 3 — Create + validation
- [x] Stage 4 — Update + delete
- [x] Stage 5 — Swagger UI
- [x] Stage 6 — README and Git history prepared
- [x] Stage 7 — AI rematch section + isolated AI version

# Task API — FlyRank Week 3 Assignment A2

A small FastAPI CRUD API upgraded from in-memory storage to a persistent SQLite database.

This project continues the Week 2 CRUD API. The API endpoints and response behavior remain the same; only the storage layer has changed from a Python list to `tasks.db`.

## Assignment goal

Week 3 requires the same CRUD API to store tasks in SQLite so data survives server restarts.

### API architecture

```text
Client
  |
  v
FastAPI CRUD API
  |
  v
SQLite (tasks.db)
```

## Tech stack

- Python 3.10+
- FastAPI
- Uvicorn
- SQLite (`sqlite3`, included with Python)
- Pytest + HTTPX
- DB Browser for SQLite

No separate database server is required.

## Why SQLite?

SQLite was chosen because it:

- stores the complete database in one file;
- requires zero database-server setup;
- is included with Python through `sqlite3`;
- keeps the project simple for a small CRUD API;
- provides persistence, so data survives application restarts.

## Database

The database file is:

```text
tasks.db
```

It is created automatically when the application starts.

The `tasks` table is also created automatically:

| Column | Type | Purpose |
|---|---|---|
| `id` | INTEGER | Primary key, automatically assigned |
| `title` | TEXT | Task title |
| `done` | INTEGER | Boolean value stored as 0 or 1 |

The database is intentionally git-ignored. A fresh clone creates its own `tasks.db` automatically.

## Seed data

On first startup, the application inserts exactly three example tasks, but only when the table is empty:

1. Learn FastAPI
2. Build CRUD API
3. Test with Swagger

Restarting the server does not duplicate these rows.

## Installation

### 1. Create a virtual environment

Windows PowerShell:

```powershell
python -m venv .venv
```

### 2. Activate it

```powershell
.\.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```powershell
pip install -r requirements.txt
```

## Start the API

```powershell
uvicorn main:app --reload
```

The API runs at:

```text
http://localhost:8000
```

Swagger UI:

```text
http://localhost:8000/docs
```

## CRUD endpoints

| Method | Endpoint | Purpose | Success | Errors |
|---|---|---|---|---|
| GET | `/` | API information | 200 | — |
| GET | `/health` | Health check | 200 | — |
| GET | `/tasks` | List all tasks | 200 | — |
| GET | `/tasks/{id}` | Get one task | 200 | 404 |
| POST | `/tasks` | Create task | 201 | 400 |
| PUT | `/tasks/{id}` | Update task | 200 | 400, 404 |
| DELETE | `/tasks/{id}` | Delete task | 204 | 404 |

The same endpoint behavior from Assignment 1 is preserved.

## Parameterized SQL

All user-supplied values are passed separately through `?` placeholders.

Examples:

```sql
SELECT * FROM tasks WHERE id = ?;
```

```sql
INSERT INTO tasks (title, done) VALUES (?, ?);
```

```sql
UPDATE tasks SET title = ?, done = ? WHERE id = ?;
```

```sql
DELETE FROM tasks WHERE id = ?;
```

This avoids building SQL strings by concatenating user input.

## Example API checks

### Read all tasks

```powershell
curl.exe -i http://localhost:8000/tasks
```

### Read one task

```powershell
curl.exe -i http://localhost:8000/tasks/1
```

### Unknown task

```powershell
curl.exe -i http://localhost:8000/tasks/999
```

Expected status: `404`.

### Create

```powershell
curl.exe -i -X POST http://localhost:8000/tasks -H "Content-Type: application/json" -d "{\"title\":\"Buy milk\"}"
```

Expected status: `201`.

### Update

```powershell
curl.exe -i -X PUT http://localhost:8000/tasks/1 -H "Content-Type: application/json" -d "{\"done\":true}"
```

Expected status: `200`.

### Delete

```powershell
curl.exe -i -X DELETE http://localhost:8000/tasks/1
```

Expected status: `204`.

## Testing

Run the automated tests:

```powershell
pytest -q
```

The tests cover:

- root and health endpoints;
- SQLite schema;
- three-task seed behavior;
- database reads;
- 404 handling;
- create validation;
- database inserts;
- updates;
- deletes;
- persistence in SQLite.

## Stage 4 — SQL explored by hand

Open `tasks.db` with DB Browser for SQLite and use the **Execute SQL** tab.

Example query:

```sql
SELECT * FROM tasks;
```

This returns every task stored in the database.

Other useful assignment queries:

```sql
SELECT * FROM tasks WHERE done = 1;
```

```sql
SELECT COUNT(*) FROM tasks;
```

After changing data in DB Browser, call:

```text
GET /tasks
```

The API reads the same SQLite file, so the change is visible without restarting the server.

## DB Browser screenshot

For the final submission, open `tasks.db` in DB Browser for SQLite and capture a screenshot showing:

- the `tasks` table;
- the columns `id`, `title`, and `done`;
- the three seed rows or your current task rows.

Save the screenshot in the repository, for example:

```text
docs/db-browser-screenshot.png
```

Then add it to this README:

```markdown
## Database screenshot

![SQLite tasks table](docs/db-browser-screenshot.png)
```

## Persistence proof

A simple persistence check:

1. Start the API.
2. Create a task.
3. Stop the API.
4. Start the API again.
5. Run `GET /tasks`.
6. Confirm the created task is still present.

This proves the data is stored in SQLite rather than only in application memory.

## Git history

The assignment asks for one commit per stage.

Recommended commit sequence:

```text
Stage 0: create SQLite database
Stage 1: database read endpoints
Stage 2: insert into database
Stage 3: update and delete with SQL
Stage 4: explored SQLite
Stage 5: database documentation
```

The repository already contains the Week 2 history; these six additional commits document the Week 3 migration.

## Clean-clone behavior

A stranger should be able to:

```powershell
git clone <YOUR-REPOSITORY-URL>
cd flyrank-crud-api
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn main:app --reload
```

The application automatically creates `tasks.db`, creates the `tasks` table, and seeds the three example tasks.

## Assignment checklist

- [x] Same CRUD endpoints as Assignment 1
- [x] SQLite database storage
- [x] `tasks.db` created automatically
- [x] `tasks` table created automatically
- [x] Three tasks seeded only when the table is empty
- [x] Data survives restarts
- [x] Parameterized SQL queries
- [x] 200 / 201 / 204 success codes
- [x] 400 validation errors
- [x] 404 unknown-task errors
- [x] README documents SQLite choice
- [x] README documents run command
- [x] README includes an example SQL query
- [ ] Add DB Browser screenshot after opening the database locally
- [ ] Complete the six Week 3 stage commits
- [ ] Push final changes to public GitHub

## Project structure

```text
flyrank-crud-api/
├── ai-version/
├── .gitignore
├── README.md
├── main.py
├── requirements.txt
└── test_main.py
```

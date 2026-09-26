# Task API — FlyRank Week 2 Assignment A1

FastAPI CRUD API for an in-memory to-do list. Swagger UI is available at `/docs`.

## Run

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

Open `http://localhost:8000/docs` for Swagger UI.

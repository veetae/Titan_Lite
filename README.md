# Titan Lite

Slim FastAPI scaffold:
- Coordinator on **9000** â†’ `/health`
- Langman stub on **9001** â†’ `/health`

## Local quickstart
```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -e .
.\.venv\Scripts\python.exe -m uvicorn api.coordinator.main:app --port 9000

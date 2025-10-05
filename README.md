<!-- Skip CMD/PowerShell errors -->
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass

<!-- Run Virtual Environment -->
.\venv\Scripts\Activate.ps1

uvicorn main:app --reload --port 8000
uvicorn main:app --reload --host 0.0.0.0 --port 8000 --log-level debug



fastapi-vue-invoice/
├─ backend/
│ ├─ main.py
│ ├─ requirements.txt
├─ frontend/
│ ├─ index.html # Vue 3 (CDN) + Axios
└─ README.md
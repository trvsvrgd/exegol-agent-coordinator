@echo off
setlocal
set ROOT=%~dp0

if exist "%ROOT%dist\exegol\exegol.exe" (
  start "" "%ROOT%dist\exegol\exegol.exe"
  exit /b 0
)

if exist "%ROOT%venv\Scripts\python.exe" (
  "%ROOT%venv\Scripts\python.exe" -m streamlit run "%ROOT%ui_dashboard.py"
  exit /b 0
)

python -m streamlit run "%ROOT%ui_dashboard.py"

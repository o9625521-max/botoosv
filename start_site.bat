@echo off
cd /d "%~dp0"
start "" "%~dp0venv\Scripts\pythonw.exe" "%~dp0webhook_site\app.py"
echo Site started on http://localhost:5000

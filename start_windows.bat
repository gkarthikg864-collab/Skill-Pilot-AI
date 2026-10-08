@echo off
cd /d "%~dp0"
echo Starting SkillPilot AI...
start "" http://127.0.0.1:8000/
python backend\server.py
pause

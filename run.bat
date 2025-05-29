@echo off
echo 啟動 AI 研究助理系統...
cd /d "%~dp0"
call venv\Scripts\activate
cd app
python main.py
pause
@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo [SnowQ] Starting han_any...
echo URL: http://localhost:5057
C:\Users\Acvin\.conda\envs\python_env\python.exe app.py
pause

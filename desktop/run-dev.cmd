@echo off
setlocal
set "PATH=C:\Program Files\nodejs;%PATH%"
for %%I in ("%~dp0..") do set "ATLAS_ROOT=%%~fI"
set "ATLAS_PYTHON=%ATLAS_ROOT%\venv\Scripts\python.exe"
if not exist "%ATLAS_PYTHON%" set "ATLAS_PYTHON=python"
netstat -ano | findstr ":8000" | findstr "LISTENING" >nul
if errorlevel 1 start "ATLAS Backend" /min "%ATLAS_PYTHON%" "%ATLAS_ROOT%\backend\server.py"
cd /d "%ATLAS_ROOT%\web-ui"
npm.cmd run dev -- --host 127.0.0.1 --port 5173

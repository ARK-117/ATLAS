@echo off
setlocal
set "PATH=C:\Program Files\nodejs;%PATH%"
cd /d "%~dp0"
cd /d "%~dp0..\web-ui"
npm.cmd run dev -- --host 127.0.0.1 --port 5173

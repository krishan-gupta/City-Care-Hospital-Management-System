@echo off
title City Care Hospital Management System - Shutdown
echo =======================================================
echo    Stopping City Care Hospital Management System
echo =======================================================
echo.

echo Stopping services on port 8000 (Backend FastAPI)...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr /r ":8000[ ]"') do (
    taskkill /f /pid %%a >nul 2>&1
)

echo Stopping services on port 5173 (Frontend React/Vite)...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr /r ":5173[ ]"') do (
    taskkill /f /pid %%a >nul 2>&1
)

echo.
echo All City Care services have been terminated.
echo.
timeout /t 2 >nul

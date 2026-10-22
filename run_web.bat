@echo off
chcp 65001 >nul
title Meta NLLB-200 AI Translator | المترجم فائق الجودة

cd /d "%~dp0"

if exist "venv\Scripts\python.exe" (
    set "PYTHON_EXE=venv\Scripts\python.exe"
) else (
    set "PYTHON_EXE=python"
)

echo =========================================================
echo   🌟 تشغيل Meta NLLB-200 AI Translator (100% أوفلاين)
echo =========================================================
echo.

"%PYTHON_EXE%" "server.py" %*

if %errorlevel% neq 0 (
    echo.
    echo [ERROR] حدث خطأ أثناء تشغيل الخادم.
    echo تأكد من تشغيل install_windows.bat أولاً.
    echo.
    pause
)

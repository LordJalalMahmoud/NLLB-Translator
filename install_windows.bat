@echo off
chcp 65001 >nul
title Meta NLLB-200 AI Translator Setup | تثبيت مترجم الذكاء الاصطناعي

echo =========================================================
echo   🌟 تثبيت برنامج Meta NLLB-200 AI Translator (Windows)
echo =========================================================
echo.

:: 1. التحقق من بايثون
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] بايثون غير مثبت أو غير مضاف لـ PATH!
    echo يرجى تنزيل وتثبيت Python من موقع python.org
    echo وتأكد من تحديد خيار: [Add Python to PATH] أثناء التثبيت.
    echo.
    pause
    exit /b 1
)

echo [*] تم العثور على بايثون بنجاح.

:: 2. إنشاء البيئة الافتراضية
if not exist "venv" (
    echo [*] جاري إنشاء البيئة الافتراضية (venv)...
    python -m venv venv
)

:: 3. تفعيل البيئة وتثبيت المتطلبات
echo [*] جاري تثبيت الحزم المطلوبة (ctranslate2, transformers, sentencepiece)...
call venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt

:: 4. تنزيل نموذج Meta NLLB-200 (600 ميجابايت لمرة واحدة)
echo.
echo [*] جاري فحص وتنزيل نموذج Meta NLLB-200...
python download_model.py

echo.
echo =========================================================
echo   ✅ اكتمل التثبيت بنجاح وجاهز للعمل بدون إنترنت 100%!
echo =========================================================
echo.
echo لتشغيل البرنامج في المتصفح: انقر مرتين على [run_web.bat]
echo.
pause

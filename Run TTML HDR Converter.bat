@echo off
setlocal
cd /d "%~dp0"

where py >nul 2>nul
if %errorlevel% equ 0 (
    set "PYTHON=py -3"
) else (
    where python >nul 2>nul
    if %errorlevel% neq 0 (
        echo Python 3 is required but was not found.
        echo Please contact IT to install Python 3 for your user account, then run this file again.
        pause
        exit /b 1
    )
    set "PYTHON=python"
)

if not exist ".venv\Scripts\python.exe" (
    %PYTHON% -m venv .venv
    if errorlevel 1 goto :error
)

".venv\Scripts\python.exe" -m pip install --disable-pip-version-check -r requirements-windows.txt
if errorlevel 1 goto :error

start "TTML HDR Converter V2" http://localhost:8501
".venv\Scripts\python.exe" -m streamlit run streamlit_app.py --server.headless true

:error
echo.
echo The TTML HDR Converter V2 could not start.
pause
exit /b 1
@echo off
setlocal
cd /d "%~dp0\..\.."

if not exist ".tmp\matplotlib" mkdir ".tmp\matplotlib"
set "MPLCONFIGDIR=%CD%\.tmp\matplotlib"

python -m PyInstaller --noconfirm --clean packaging\windows\TECLA.spec
if errorlevel 1 exit /b %errorlevel%

echo.
echo Ejecutable generado en:
echo   %CD%\dist\TECLA.exe

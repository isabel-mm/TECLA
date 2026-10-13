@echo off
setlocal
cd /d "%~dp0\..\.."

if not exist ".tmp\matplotlib" mkdir ".tmp\matplotlib"
set "MPLCONFIGDIR=%CD%\.tmp\matplotlib"

rem Listas de stopwords de NLTK: se incluyen en la aplicacion
python -c "import nltk; nltk.download('stopwords', quiet=True)"

python -m PyInstaller --noconfirm --clean packaging\windows\TECLA.spec
if errorlevel 1 exit /b %errorlevel%

rem Carpeta comprimida, lista para distribuir
powershell -NoProfile -Command "Compress-Archive -Path 'dist\TECLA' -DestinationPath 'dist\TECLA-windows.zip' -Force"
if errorlevel 1 exit /b %errorlevel%

rem Instalador (necesita Inno Setup 6: winget install JRSoftware.InnoSetup)
set "ISCC=%LOCALAPPDATA%\Programs\Inno Setup 6\ISCC.exe"
if not exist "%ISCC%" set "ISCC=%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe"
if exist "%ISCC%" (
    "%ISCC%" /Q packaging\windows\TECLA.iss
    if errorlevel 1 exit /b 1
    echo Instalador generado en:
    echo   %CD%\dist\TECLA-2.0.0-setup.exe
) else (
    echo Inno Setup no esta instalado: no se genera el instalador.
)

echo.
echo Aplicacion generada en:
echo   %CD%\dist\TECLA\TECLA.exe
echo Comprimida para distribuir en:
echo   %CD%\dist\TECLA-windows.zip

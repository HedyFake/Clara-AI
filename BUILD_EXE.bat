@echo off
setlocal EnableExtensions
cd /d "%~dp0"

rem =====================================================================
rem  Build ClaraDesktopBuddy.exe dengan PyInstaller
rem  - Build folder ditaruh di dalam proyek (%~dp0build), bukan %TEMP%
rem  - Otomatis bersihkan folder build & spec lama sebelum build
rem  - Otomatis bersihkan file .spec & .exe lama di root
rem =====================================================================

rem --- Normalisasi ROOT (buang backslash terakhir agar tidak makan kutip) ---
set "ROOT=%~dp0"
if "%ROOT:~-1%"=="\" set "ROOT=%ROOT:~0,-1%"

set "BUILD_DIR=%ROOT%\build"
set "SPEC_DIR=%ROOT%\build\spec"
set "WORK_DIR=%ROOT%\build\work"

echo [1/4] Membersihkan folder build lama...
if exist "%BUILD_DIR%" (
    rmdir /s /q "%BUILD_DIR%" 2>nul
    if exist "%BUILD_DIR%" (
        echo      WARNING: Folder build tidak bisa dihapus sepenuhnya.
        echo      Mencoba takeown + icacls...
        takeown /f "%BUILD_DIR%" /r /d y >nul 2>&1
        icacls "%BUILD_DIR%" /grant administrators:F /t >nul 2>&1
        rmdir /s /q "%BUILD_DIR%" 2>nul
    )
)
if exist "%ROOT%\ClaraDesktopBuddy.spec" del /f /q "%ROOT%\ClaraDesktopBuddy.spec" >nul 2>&1
if exist "%ROOT%\ClaraDesktopBuddy.exe"  del /f /q "%ROOT%\ClaraDesktopBuddy.exe"  >nul 2>&1

rem --- Pastikan Python lokal ada ---
echo [2/4] Memeriksa Python lokal (.venv)...
if not exist ".venv\Scripts\python.exe" (
    echo      .venv belum ada, menjalankan INSTALL_CLARA.bat...
    call INSTALL_CLARA.bat
    if errorlevel 1 (
        echo GAGAL: Instalasi dependensi gagal.
        pause
        exit /b 1
    )
)

rem --- Buat folder build ---
if not exist "%BUILD_DIR%" mkdir "%BUILD_DIR%"
if not exist "%SPEC_DIR%"  mkdir "%SPEC_DIR%"
if not exist "%WORK_DIR%"  mkdir "%WORK_DIR%"

rem --- Jalankan PyInstaller ---
echo [3/4] Menjalankan PyInstaller...
".venv\Scripts\python.exe" -m PyInstaller --noconfirm --clean --onefile --windowed ^
  --name ClaraDesktopBuddy ^
  --icon "%ROOT%\assets\clara.ico" ^
  --add-data "%ROOT%\assets;assets" ^
  --distpath "%ROOT%" ^
  --workpath "%WORK_DIR%" ^
  --specpath "%SPEC_DIR%" ^
  --add-data "%ROOT%\memory_profile.md;." ^
  --add-data "%ROOT%\MEMORY_TRANSFER_PROMPT_ID.md;." ^
  --add-data "%ROOT%\MEMORY_SCHEMA.json;." ^
  --add-data "%ROOT%\PORTABLE_MEMORY_README_ID.md;." ^
  --add-data "%ROOT%\FEATURE_CATALOG_ID.md;." ^
  --add-data "%ROOT%\FEATURE_CATALOG_ID.csv;." ^
  --add-data "%ROOT%\TOKEN_OPTIMIZATION_PLAYBOOK_ID.md;." ^
  --hidden-import clara_core ^
  --hidden-import clara_avatar ^
  --hidden-import clara_finance ^
  --hidden-import clara_market ^
  --collect-all requests ^
  --hidden-import pyttsx3.drivers.sapi5 ^
  --hidden-import pythoncom ^
  --hidden-import pywintypes ^
  --collect-all speech_recognition ^
  --collect-all comtypes ^
  --collect-all pyaudio ^
  --paths "%ROOT%" ^
  "%ROOT%\clara_buddy.py"

if errorlevel 1 (
    echo.
    echo ============================================================
    echo  BUILD GAGAL. Baca pesan PyInstaller di atas.
    echo  Folder build ada di: %BUILD_DIR%
    echo ============================================================
    pause
    exit /b 1
)

echo.
echo ============================================================
echo [4/4] BUILD SUKSES
echo  EXE: %ROOT%\ClaraDesktopBuddy.exe
echo  Folder build (bisa dihapus kapan saja): %BUILD_DIR%
echo  Aplikasi TIDAK mengatur startup Windows.
echo ============================================================
pause
exit /b 0
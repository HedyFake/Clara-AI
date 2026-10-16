@echo off
setlocal
cd /d "%~dp0"

rem 1) Versi source (selalu paling baru)
if exist "%~dp0.venv\Scripts\pythonw.exe" (
  start "Clara" "%~dp0.venv\Scripts\pythonw.exe" "%~dp0clara_buddy.py"
  exit /b 0
)
rem 2) EXE hasil BUILD_EXE.bat
if exist "%~dp0ClaraDesktopBuddy.exe" (
  start "Clara" "%~dp0ClaraDesktopBuddy.exe"
  exit /b 0
)
rem 3) Belum terpasang: pasang otomatis lalu jalankan
echo Pertama kali: memasang dependensi Clara (butuh internet, +/- 2 menit)...
call "%~dp0INSTALL_CLARA.bat" /auto
if errorlevel 1 exit /b 1
start "Clara" "%~dp0.venv\Scripts\pythonw.exe" "%~dp0clara_buddy.py"
exit /b 0

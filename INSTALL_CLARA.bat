@echo off
setlocal
cd /d "%~dp0"

set "PY="
where py >nul 2>nul
if not errorlevel 1 (
  py -3.12 --version >nul 2>nul
  if not errorlevel 1 set "PY=py -3.12"
  if not defined PY (
    py -3.11 --version >nul 2>nul
    if not errorlevel 1 set "PY=py -3.11"
  )
)
if not defined PY (
  where python >nul 2>nul
  if not errorlevel 1 set "PY=python"
)
if not defined PY (
  echo Python 3.11 atau 3.12 64-bit tidak ditemukan.
  echo Instal dari https://www.python.org/downloads/windows/ lalu jalankan ulang file ini.
  pause
  exit /b 1
)

%PY% -c "import sys; raise SystemExit(0 if sys.version_info[:2] in ((3,11),(3,12)) else 1)"
if errorlevel 1 (
  echo Clara memerlukan Python 3.11 atau 3.12.
  %PY% --version
  pause
  exit /b 1
)

if not exist ".venv\Scripts\python.exe" (
  %PY% -m venv .venv
  if errorlevel 1 goto :failed
)
".venv\Scripts\python.exe" -m pip install --upgrade pip
if errorlevel 1 goto :failed
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 goto :failed

echo Dependensi Clara siap di folder lokal .venv.
if /i not "%~1"=="/auto" (
  echo Jalankan START_CLARA.bat untuk memulai.
  pause
)
exit /b 0

:failed
echo Instalasi dependensi gagal. Baca pesan pip di atas; tidak ada perubahan sistem/admin.
echo Jika PyAudio gagal: Clara tetap jalan tanpa mikrofon (hapus baris PyAudio di requirements.txt lalu ulangi).
pause
exit /b 1

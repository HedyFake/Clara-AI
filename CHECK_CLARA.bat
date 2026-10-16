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
if not defined PY set "PY=python"
%PY% audit_clara.py
if errorlevel 1 (
  echo Audit statis gagal. Baca error di atas.
  pause
  exit /b 1
)
echo Audit statis selesai. Ini tidak menggantikan tes nyata di Windows.
pause

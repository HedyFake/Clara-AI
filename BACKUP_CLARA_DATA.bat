@echo off
setlocal
set "SRC=%LOCALAPPDATA%\ClaraDesktopBuddy"
if not exist "%SRC%" (
  echo Folder data Clara belum ada: "%SRC%"
  pause
  exit /b 1
)
for /f %%i in ('powershell -NoProfile -Command "Get-Date -Format yyyyMMdd_HHmmss"') do set "STAMP=%%i"
set "DEST=%USERPROFILE%\Documents\ClaraBackup_%STAMP%"
mkdir "%DEST%" 2>nul
xcopy "%SRC%\*" "%DEST%\" /E /I /H /Y
if errorlevel 1 (
  echo Backup mungkin tidak lengkap. Periksa log di atas.
  pause
  exit /b 1
)
echo Backup data Clara disalin ke:
echo "%DEST%"
echo PERINGATAN: folder dapat berisi jurnal chat, konteks usaha, screenshot, dan judul aplikasi. Simpan secara pribadi.
pause

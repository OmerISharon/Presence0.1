@echo off
setlocal

:: Set source and backup base directories
set "SOURCE_DIR=C:\Users\omers\AppData\Local\Google\Chrome Beta\User Data"
set "BACKUP_BASE=D:\2025\Projects\Presence\Presence0.1\Resources\Important_Backups\Chrome_Beta_Profiles"

:: Extract current date and format as YYYY-MM-DD
for /f "tokens=2 delims= " %%a in ('date /t') do set "TODAY=%%a"
for /f "tokens=1-3 delims=/" %%a in ("%TODAY%") do (
    set "MM=%%a"
    set "DD=%%b"
    set "YYYY=%%c"
)

set "DATE_FOLDER=%YYYY%-%MM%-%DD%"
set "DEST_DIR=%BACKUP_BASE%\%DATE_FOLDER%"

:: Create backup destination folder
mkdir "%DEST_DIR%"

echo Backing up Chrome Beta profiles...

:: Loop through all "Profile*" folders
for /d %%P in ("%SOURCE_DIR%\Profile*") do (
    echo Backing up %%~nxP...
    xcopy "%%P" "%DEST_DIR%\%%~nxP" /E /I /Y >nul
)

echo All profiles backed up to: %DEST_DIR%
endlocal

@echo off
setlocal

:: Set backup base path
set "BACKUP_DIR=D:\2025\Projects\Presence\Presence0.1\Resources\Important_Backups\Chrome_Beta_Local_State"

:: Extract date components
for /f "tokens=2 delims= " %%a in ('date /t') do set "DATE=%%a"
:: Split the date (MM/DD/YYYY or DD/MM/YYYY depending on locale)
for /f "tokens=1-3 delims=/" %%a in ("%DATE%") do (
    set "MM=%%a"
    set "DD=%%b"
    set "YYYY=%%c"
)

:: Final timestamp in format YYYY-MM-DD
set "TIMESTAMP=%YYYY%-%MM%-%DD%"
set "DEST_FOLDER=%BACKUP_DIR%\%TIMESTAMP%"

:: Source file
set "SOURCE_FILE=%LOCALAPPDATA%\Google\Chrome Beta\User Data\Local State"

:: Create backup folder
mkdir "%DEST_FOLDER%"

:: Copy file
copy "%SOURCE_FILE%" "%DEST_FOLDER%\Local State" >nul

echo Backup completed to: %DEST_FOLDER%
endlocal

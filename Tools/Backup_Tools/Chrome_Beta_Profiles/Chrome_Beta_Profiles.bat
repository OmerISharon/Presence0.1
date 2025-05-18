@echo off
setlocal enabledelayedexpansion

:: Configuration
set "SOURCE_DIR=C:\Users\omers\AppData\Local\Google\Chrome Beta\User Data"
set "BACKUP_BASE=D:\2025\Projects\Presence\Presence0.1\Resources\Important_Backups\Chrome_Beta_Profiles"
set "MAX_BACKUPS=3"

:: Get current date formatted as YYYY-MM-DD
for /f "tokens=2 delims= " %%a in ('date /t') do set "TODAY=%%a"
for /f "tokens=1-3 delims=/" %%a in ("%TODAY%") do (
    set "MM=%%a"
    set "DD=%%b"
    set "YYYY=%%c"
)
set "DATE_FOLDER=%YYYY%-%MM%-%DD%"
set "DEST_DIR=%BACKUP_BASE%\%DATE_FOLDER%"

:: Create backup folder
mkdir "%DEST_DIR%"

echo Backing up Chrome Beta profiles...

:: Copy all Profile* folders
for /d %%P in ("%SOURCE_DIR%\Profile*") do (
    echo Backing up %%~nxP...
    xcopy "%%P" "%DEST_DIR%\%%~nxP" /E /I /Y >nul
)

echo All profiles backed up to: %DEST_DIR%

:: -----------------------
:: Clean up older backups
:: -----------------------

echo Checking for old backups to delete...

:: List folders in descending date order (most recent first)
pushd "%BACKUP_BASE%"
set count=0

for /f "delims=" %%F in ('dir /ad /b /o-d') do (
    set /a count+=1
    if !count! GTR %MAX_BACKUPS% (
        echo Deleting old backup: %%F
        rmdir /s /q "%%F"
    )
)
popd

echo Done. Kept the last %MAX_BACKUPS% backups only.

endlocal

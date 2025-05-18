@echo off
setlocal enabledelayedexpansion

:: Configuration
set "BACKUP_DIR=D:\2025\Projects\Presence\Presence0.1\Resources\Important_Backups\Chrome_Beta_Local_State"
set "MAX_BACKUPS=5"
set "SOURCE_FILE=%LOCALAPPDATA%\Google\Chrome Beta\User Data\Local State"

:: Extract date components
for /f "tokens=2 delims= " %%a in ('date /t') do set "DATE=%%a"
for /f "tokens=1-3 delims=/" %%a in ("%DATE%") do (
    set "MM=%%a"
    set "DD=%%b"
    set "YYYY=%%c"
)

:: Final timestamp as folder name
set "TIMESTAMP=%YYYY%-%MM%-%DD%"
set "DEST_FOLDER=%BACKUP_DIR%\%TIMESTAMP%"

:: Create folder and copy file
mkdir "%DEST_FOLDER%"
copy "%SOURCE_FILE%" "%DEST_FOLDER%\Local State" >nul
echo Backup completed to: %DEST_FOLDER%

:: -----------------------
:: Clean up old backups
:: -----------------------

echo Checking for old backups to delete...

pushd "%BACKUP_DIR%"
set count=0

:: Loop through folders sorted newest to oldest
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

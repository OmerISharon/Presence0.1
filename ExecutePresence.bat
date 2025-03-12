@echo off
setlocal enabledelayedexpansion

REM Set the base channels directory.
set "channels_dir=D:\2025\Projects\Presence\Presence0.1\Channels"

REM Loop through all subdirectories in the channels directory.
for /d %%F in ("%channels_dir%\*") do (
    REM Get the folder name (without the full path).
    set "folderName=%%~nF"
    REM Check if the folder name contains the string "(not in use)".
    echo !folderName! | findstr /C:"(not in use)" >nul
    if errorlevel 1 (
        echo Processing folder: !folderName!
        REM Run the channel-specific batch file first.
        call "D:\2025\Projects\Presence\Presence0.1\Channels\!folderName!\Batch\!folderName!.bat"
        REM Then call the uploader script with the channel name as argument.
        py "D:\2025\Projects\Presence\Presence0.1\Uploader\main.py" "!folderName!"
    ) else (
        echo Skipping folder: !folderName! (contains "(not in use)")
    )
)

exit

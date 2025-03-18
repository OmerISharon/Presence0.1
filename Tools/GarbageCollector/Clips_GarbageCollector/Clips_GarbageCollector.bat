@echo off
setlocal enabledelayedexpansion

:: Set base paths
set "CHANNELS_DIR=D:\2025\Projects\Presence\Presence0.1\Channels"
set "LOGS_DIR=D:\2025\Projects\Presence\Presence0.1\Tools\GarbageCollector\Clips_GarbageCollector\Logs"

:: Create logs directory if it doesn't exist
if not exist "%LOGS_DIR%" mkdir "%LOGS_DIR%"

:: Generate log filename with current timestamp
for /f "tokens=2 delims==" %%I in ('wmic os get localdatetime /value') do set datetime=%%I
set "LOG_FILE=%LOGS_DIR%\GarbageCollector_%datetime:~0,14%.log"

:: Start logging
echo Garbage Collector Started: %date% %time% > "%LOG_FILE%"
echo ---------------------------------------- >> "%LOG_FILE%"

:: Counter for deleted folders
set "deleted_folders_count=0"

:: Scan through channels
for /D %%D in ("%CHANNELS_DIR%\*") do (
    set "channel_name=%%~nxD"
    
    :: Skip folders ending with "(not in use)"
    echo !channel_name! | findstr /R /C:"(not in use)$" >nul
    if errorlevel 1 (
        set "clips_dir=%CHANNELS_DIR%\!channel_name!\Clips"
        
        if exist "!clips_dir!" (
            :: Reset channel deletion count
            set "channel_deleted_count=0"
            
            :: Temporarily store deleted folders
            set "deleted_folders_temp=%TEMP%\deleted_folders_!channel_name!.txt"
            
            :: Scan subfolders in Clips directory
            for /D %%S in ("!clips_dir!\*") do (
                set "subfolder=%%S"
                
                :: Use dir command to check for MP4 files
                dir "!subfolder!\*.mp4" /b /s >nul 2>&1
                if errorlevel 1 (
                    :: Log to both console and log file
                    if !channel_deleted_count! equ 0 (
                        echo Channel: !channel_name! >> "%LOG_FILE%"
                        echo Channel: !channel_name!
                    )
                    
                    :: Log deleted folder
                    echo !subfolder! >> "%LOG_FILE%"
                    echo !subfolder!
                    
                    :: Delete the folder
                    rmdir /S /Q "!subfolder!"
                    
                    :: Increment counters
                    set /a deleted_folders_count+=1
                    set /a channel_deleted_count+=1
                )
            )
            
            :: Add a blank line after each channel's deletions
            if !channel_deleted_count! gtr 0 (
                echo. >> "%LOG_FILE%"
                echo.
            )
        )
    )
)

:: Log summary
echo ---------------------------------------- >> "%LOG_FILE%"
echo Total Folders Deleted: %deleted_folders_count% >> "%LOG_FILE%"
echo Garbage Collector Completed: %date% %time% >> "%LOG_FILE%"

:: Keep console window open briefly
timeout /t 5 >nul

exit
@echo off
setlocal EnableDelayedExpansion

rem Change to the folder containing Channel_Uploader.py
cd /d "D:\2025\Projects\Presence\Presence0.1\Uploader\Code\Channel_Uploader"

rem Loop over each folder in the Channels directory
for /d %%a in ("D:\2025\Projects\Presence\Presence0.1\Channels\*") do (
    set "CHANNAME=%%~nxa"
    rem Skip folders that end with "(not in use)"
    if /i "!CHANNAME:~-12!"=="(not in use)" (
         echo Skipping folder: !CHANNAME!
    ) else (
         "C:\Users\omers\AppData\Local\Programs\Python\Python311\python.exe" Channel_Uploader.py "!CHANNAME!"
    )
)

exit /b

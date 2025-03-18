@echo off

REM Change directory to the Youtube API POC folder
cd /d "D:\2025\Projects\Presence\Presence0.1\Tools\PresenceDashboard\Youtube_API_POC\"

REM Run the POC Platform Engagement Poller and wait for it to complete
start /wait "" "POC-Platform-Engagement-Poller.exe"

REM Change directory to the PresenceDashboard folder
cd /d "D:\2025\Projects\Presence\Presence0.1\Tools\PresenceDashboard\PresenceDashboard\"

REM Run npm start
npm start

REM Keep the window open after executing
pause
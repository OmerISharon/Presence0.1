@echo off

REM Change directory to the Youtube API POC folder
cd /d "D:\2025\Projects\Presence\Presence0.1\Tools\PresenceDashboard\Platform-Engagement-Poller"

REM Run the POC Platform Engagement Poller and wait for it to complete
start /wait "" "POC-Platform-Engagement-Poller.exe"

exit
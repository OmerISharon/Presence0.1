@echo off
REM Define path to appsettings.json
set SETTINGS="D:\2025\Projects\Presence\Presence0.1\Tools\PresenceDashboard\Platform-Engagement-Poller\AppsSettings\appsettings.json"

REM Run the EXE
D:
cd D:\2025\Projects\Presence\Presence0.1\Tools\PresenceDashboard\PresenceAddNewAccount
start "" "PresenceAddNewAccount.exe" %SETTINGS%
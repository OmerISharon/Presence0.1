@echo off
REM Disabling Google Chrome Beta Elevation Service
sc stop "GoogleChromeBetaElevationService"
sc config "GoogleChromeBetaElevationService" start= disabled

REM Disabling Google Chrome Elevation Service
sc stop "GoogleChromeElevationService"
sc config "GoogleChromeElevationService" start= disabled

REM Disabling Google Updater Internal Service
sc stop "GoogleUpdaterInternalService135.0.7023.0"
sc config "GoogleUpdaterInternalService135.0.7023.0" start= disabled

REM Disabling Google Updater Service
sc stop "GoogleUpdaterService135.0.7023.0"
sc config "GoogleUpdaterService135.0.7023.0" start= disabled

echo All specified services have been disabled.
pause

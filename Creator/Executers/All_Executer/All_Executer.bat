@echo off
setlocal EnableDelayedExpansion

:: -------------------------------
:: Display the batch file's name in uppercase as a title
:: -------------------------------
for /f "delims=" %%A in ('powershell -NoProfile -Command "Write-Output '%~nx0'.ToUpper()"') do set BATCHNAME=%%A
echo ===========================
echo %BATCHNAME%
echo ===========================
echo.

:: -------------------------------
:: Set Channels Directory
:: -------------------------------
set "CHANNELSDIR=D:\2025\Projects\Presence\Presence0.1\Creator\Channels"
echo CHANNELSDIR is: %CHANNELSDIR%
echo.

:: -------------------------------
:: Loop through each channel folder and run its executer batch file
:: -------------------------------
for /D %%I in ("%CHANNELSDIR%\*") do (
    set "CHANNAME=%%~nI"
    echo Processing channel: !CHANNAME!
    set "EXECPATH=%CHANNELSDIR%\!CHANNAME!\Executer\!CHANNAME!.bat"
    echo Checking executer file at: !EXECPATH!
    if exist "!EXECPATH!" (
        echo Executer found for channel: !CHANNAME!. Executing...
        call "!EXECPATH!"
        echo Completed channel: !CHANNAME!
    ) else (
        echo Executer not found for channel: !CHANNAME!
    )
    echo.
)

echo All channels processed.

exit /b

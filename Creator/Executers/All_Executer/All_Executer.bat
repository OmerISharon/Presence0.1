@echo off
setlocal EnableDelayedExpansion

:: -------------------------------
:: Display the batch file's name in uppercase as a title
:: -------------------------------
for /f "delims=" %%A in ('powershell -NoProfile -Command "[System.IO.Path]::GetFileName('%~nx0').ToUpper()"') do set BATCHNAME=%%A
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
    set "EXECPATH=%CHANNELSDIR%\%%~nI\Executer\%%~nI.bat"

    call :ProcessChannel
)
goto :eof

:ProcessChannel
:: Skip folders ending with "(not in use)"
echo !CHANNAME! | findstr /R /C:"(not in use)$" >nul
if !errorlevel! equ 0 (
    echo Skipping channel: !CHANNAME! (marked as not in use)
) else (
    echo Processing channel: !CHANNAME!
    echo Checking executer file at: !EXECPATH!
    if exist "!EXECPATH!" (
        echo Executer found for channel: !CHANNAME!. Executing...
        call "!EXECPATH!"
        echo Completed channel: !CHANNAME!
    ) else (
        echo Executer not found for channel: !CHANNAME!
    )
)
echo.
exit /b

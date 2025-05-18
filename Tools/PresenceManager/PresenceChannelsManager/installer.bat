@echo off
setlocal

:: Set the folder where the Python script and the shortcut reside.
set "TARGET_FOLDER=D:\2025\Projects\Presence\Presence0.1\Tools\PresenceManager\PresenceChannelsManager"
:: Name of the Python script.
set "SCRIPT_NAME=PresenceChannelsManager.py"
:: Full path to your Python interpreter (using pythonw.exe instead).
set "PYTHON_PATH=C:\Users\omers\AppData\Local\Programs\Python\Python311\pythonw.exe"
:: Shortcut file name.
set "SHORTCUT_NAME=PresenceChannelsManager.lnk"
:: Custom icon path.
set "ICON_PATH=D:\2025\Projects\Presence\Presence0.1\Tools\PresenceManager\PresenceChannelsManager\Uriy1966-Wooden-System.ico"

:: Create the shortcut using PowerShell.
powershell -NoProfile -Command ^
  "$s = (New-Object -ComObject WScript.Shell).CreateShortcut('%TARGET_FOLDER%\%SHORTCUT_NAME%'); $s.TargetPath='%PYTHON_PATH%'; $s.Arguments='%TARGET_FOLDER%\%SCRIPT_NAME%'; $s.WorkingDirectory='%TARGET_FOLDER%'; $s.Save()"

echo Shortcut created in %TARGET_FOLDER%.
pause
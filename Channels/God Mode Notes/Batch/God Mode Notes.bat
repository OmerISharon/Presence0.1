@echo off

cd /d "C:\Presence\Presence0.1\Creator\God Mode Notes\Code"
python Creator_GodModeNotes.py

cd /d "C:\Presence\Presence0.1\Uploader\Youtube\main"
python main.py "God Mode Notes"

exit
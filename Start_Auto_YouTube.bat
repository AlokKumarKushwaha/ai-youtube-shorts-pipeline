@echo off
title AI YouTube Shorts 24x7 Auto-Pilot
color 0A

echo =======================================================
echo     AI YOUTUBE SHORTS 24x7 AUTO-PILOT SYSTEM
echo =======================================================
echo.
echo [!] Har 4 ghante me taza khabar ka video banakar YouTube par auto-upload hoga...
echo [!] Band karne ke liye ye window close kar de.
echo.

cd /d "C:\Users\v9919\.gemini\antigravity\scratch\ai_shorts_pipeline"

:LOOP
echo [%date% %time%] [*] Nayi taza news ka Shorts video banakar YouTube par upload kiya ja raha hai...
python main.py --category tech --anchor male --upload

echo.
echo [%date% %time%] [+] Video upload ho gaya! Agli taza khabar ke liye 4 ghante (14400 sec) wait kar rahe hai...
echo.

rem 14400 seconds = 4 hours (testing ke liye chhota bhi kar sakte hai)
timeout /t 14400 /nobreak

goto LOOP

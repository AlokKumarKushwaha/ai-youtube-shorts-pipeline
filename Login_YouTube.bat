@echo off
title YouTube Channel Link Wizard
color 0B

echo =======================================================
echo      LINK YOUR YOUTUBE CHANNEL (ONE-TIME SETUP)
echo =======================================================
echo.
echo [*] Opening Google Login in your Chrome browser...
echo [*] Apne "Quick News Hindi" wale Google account se login karke Allow par click kare.
echo.

cd /d "C:\Users\v9919\.gemini\antigravity\scratch\ai_shorts_pipeline"
python setup_youtube.py

echo.
pause

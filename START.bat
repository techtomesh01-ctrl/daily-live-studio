@echo off
title DAILY LIVE STUDIO
cd /d "%~dp0"
where py >nul 2>nul
if errorlevel 1 (
  echo Python install nahi hai. https://www.python.org/downloads/ se Python install karein.
  pause
  exit /b 1
)
where ffmpeg >nul 2>nul
if errorlevel 1 (
  echo FFmpeg PATH mein nahi mila. README-HI.md ke FFmpeg steps follow karein.
  pause
  exit /b 1
)
if not exist .venv py -m venv .venv
call .venv\Scripts\activate.bat
py -m pip install --upgrade pip
py -m pip install -r requirements.txt
echo DAILY LIVE STUDIO: http://127.0.0.1:5000
start "" http://127.0.0.1:5000
py app.py
pause

@echo off
setlocal
cd /d "%~dp0"
title HM Portfolio - Timeline Editor

where py >nul 2>nul
if %errorlevel%==0 (
  py -3 "%~dp0timeline_editor.py"
) else (
  where python >nul 2>nul
  if %errorlevel%==0 (
    python "%~dp0timeline_editor.py"
  ) else (
    echo Python was not found.
    pause
  )
)

endlocal

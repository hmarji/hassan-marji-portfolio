@echo off
setlocal
title HM Smart Scroll V5
cd /d "%~dp0"

echo HM Smart Scroll V5
echo ------------------
echo.

if not exist "apply_smart_scroll_v5.py" (
  echo ERROR: apply_smart_scroll_v5.py is missing.
  pause
  exit /b 1
)

py "apply_smart_scroll_v5.py"
echo.
pause

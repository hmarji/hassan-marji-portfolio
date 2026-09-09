@echo off
setlocal
title HM Portfolio - HMP Style Refresh V7
cd /d "%~dp0"

echo HM Portfolio - HMP Style Refresh V7
echo -----------------------------------
echo.

if not exist "apply_hmp_style_refresh_v7.py" (
  echo ERROR: apply_hmp_style_refresh_v7.py is missing.
  pause
  exit /b 1
)

py "apply_hmp_style_refresh_v7.py"

echo.
echo TEST LOCALLY BEFORE PUSHING:
echo 1. Fresh-open index.html - it must start at the hero.
echo 2. Scroll to Practice, Knowledge, or Life in Images.
echo 3. Press F5 - it must remain there without showing the top first.
echo 4. Click Home and other menu links - normal smooth navigation must still work.
echo.
pause

@echo off
setlocal
cd /d "%~dp0"
title HM Portfolio - Life Timeline Patch

echo.
echo ============================================================
echo   HM PORTFOLIO - LIFE TIMELINE PATCH
echo ============================================================
echo.
echo This fixes thumbnail-to-viewer selection and adds:
echo   - date + caption under every thumbnail
echo   - larger date + caption beside the selected image
echo   - an editable js\life-timeline-data.js file
echo.
echo A backup will be created automatically.
echo.

where py >nul 2>nul
if %errorlevel%==0 (
    py -3 "%~dp0APPLY_LIFE_TIMELINE_PATCH.py"
) else (
    where python >nul 2>nul
    if %errorlevel%==0 (
        python "%~dp0APPLY_LIFE_TIMELINE_PATCH.py"
    ) else (
        echo ERROR: Python was not found.
        pause
        exit /b 1
    )
)

if errorlevel 1 (
    echo.
    echo Patch failed. Nothing was pushed anywhere.
    pause
    exit /b 1
)

echo.
echo ------------------------------------------------------------
echo TEST LOCALLY FIRST:
echo   Open index.html and click several timeline thumbnails.
echo.
echo EDIT DATES/CAPTIONS HERE:
echo   js\life-timeline-data.js
echo.
echo THEN, when correct:
echo   git status
echo   git add -A
echo   git commit -m "Fix life timeline viewer and add metadata"
echo   git push origin main
echo ------------------------------------------------------------
echo.
pause
endlocal

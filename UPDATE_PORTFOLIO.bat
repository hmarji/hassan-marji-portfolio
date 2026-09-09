@echo off
setlocal EnableExtensions
cd /d "%~dp0"
title HM Portfolio - Update Portfolio

echo.
echo ==============================================================
echo   HM PORTFOLIO - UPDATE PORTFOLIO
echo ==============================================================
echo.

if not exist "index.html" (
    echo ERROR: index.html was not found.
    echo Put UPDATE_PORTFOLIO.bat and update_portfolio.py
    echo in the MAIN HM Portfolio folder beside index.html.
    echo.
    pause
    exit /b 1
)

if not exist "update_portfolio.py" (
    echo ERROR: update_portfolio.py was not found beside this batch file.
    echo.
    pause
    exit /b 1
)

set "PY_CMD="
set "PY_ARGS="

where py >nul 2>nul
if not errorlevel 1 (
    set "PY_CMD=py"
    set "PY_ARGS=-3"
    goto :python_found
)

where python >nul 2>nul
if not errorlevel 1 (
    set "PY_CMD=python"
    set "PY_ARGS="
    goto :python_found
)

echo ERROR: Python 3 was not found on this computer.
echo Install Python 3, then run this file again.
echo.
pause
exit /b 1

:python_found
echo Python found.
echo Checking image optimizer...

%PY_CMD% %PY_ARGS% -c "import PIL" >nul 2>nul
if errorlevel 1 (
    echo Pillow is not installed.
    echo Trying to install Pillow for small WebP thumbnails and previews...
    %PY_CMD% %PY_ARGS% -m pip install --user Pillow
    if errorlevel 1 (
        echo.
        echo WARNING: Pillow could not be installed.
        echo The gallery will still update, but images may use originals.
        echo You can install it later with:
        echo   %PY_CMD% %PY_ARGS% -m pip install --user Pillow
        echo.
    ) else (
        echo Pillow installed successfully.
    )
) else (
    echo Pillow is ready.
)

echo.
echo Updating gallery data and optimized images...
echo.

%PY_CMD% %PY_ARGS% "update_portfolio.py"
set "RESULT=%ERRORLEVEL%"

if not "%RESULT%"=="0" (
    echo.
    echo ==============================================================
    echo UPDATE FAILED.
    echo Nothing was pushed to GitHub.
    echo ==============================================================
    echo.
    pause
    exit /b %RESULT%
)

echo.
echo ==============================================================
echo UPDATE COMPLETE.
echo ==============================================================
echo.
echo 1. Open index.html and test the website locally.
echo 2. If everything is correct, push with:
echo.
echo    git add -A
echo    git commit -m "Update portfolio images"
echo    git push origin main
echo.
echo This updater NEVER pushes automatically.
echo.
pause
endlocal

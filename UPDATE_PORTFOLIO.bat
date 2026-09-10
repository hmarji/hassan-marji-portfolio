@echo off
setlocal EnableExtensions
cd /d "%~dp0"
title HM Portfolio - Update Portfolio

echo.
echo ==============================================================
echo   HM PORTFOLIO - UPDATE AND SYNC IMAGES
echo ==============================================================
echo.
echo ONE SOURCE OF TRUTH:
echo   Selected Work : images\selected-work\
echo   Practice      : images\practice\CATEGORY\
echo   Knowledge     : images\knowledge\CATEGORY\
echo.
echo Categories:
echo   engineering
 echo   painting
 echo   photography
 echo   graphic-design
 echo   animation
 echo   training
 echo.
echo Do NOT manually edit images\thumbs or images\previews.
echo.

if not exist "index.html" (
    echo ERROR: index.html was not found.
    echo Put UPDATE_PORTFOLIO.bat in the MAIN HM Portfolio folder.
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

if not exist "sync_portfolio_folders.py" (
    echo ERROR: sync_portfolio_folders.py was not found beside this batch file.
    echo Run git pull origin main first, then try again.
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
echo.
echo [1/4] Normalizing old folders and names...
echo.

%PY_CMD% %PY_ARGS% "sync_portfolio_folders.py" --migrate
if errorlevel 1 goto :failed

echo.
echo [2/4] Checking image optimizer...

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
echo [3/4] Rebuilding gallery data and optimized images...
echo.

%PY_CMD% %PY_ARGS% "update_portfolio.py"
if errorlevel 1 goto :failed

echo.
echo [4/4] Removing unused generated thumbnails and previews...
echo.

%PY_CMD% %PY_ARGS% "sync_portfolio_folders.py" --cleanup
if errorlevel 1 goto :failed

echo.
echo ==============================================================
echo UPDATE COMPLETE.
echo ==============================================================
echo.
echo From now on, manage gallery images ONLY here:
echo.
echo   images\selected-work\
echo.
echo   images\practice\engineering\
echo   images\practice\painting\
echo   images\practice\photography\
echo   images\practice\graphic-design\
echo   images\practice\animation\
echo   images\practice\training\
echo.
echo   images\knowledge\engineering\
echo   images\knowledge\painting\
echo   images\knowledge\photography\
echo   images\knowledge\graphic-design\
echo   images\knowledge\animation\
echo   images\knowledge\training\
echo.
echo Old names such as education, architecture, graphic and images\originals
 echo are migrated automatically into the canonical folders.
echo.
echo NEXT:
echo   1. Open index.html and test the website locally.
echo   2. Run git status and review the first migration carefully.
echo   3. If everything is correct, use PUSH_PORTFOLIO.bat.
echo.
echo This updater NEVER pushes automatically.
echo.
pause
endlocal
exit /b 0

:failed
echo.
echo ==============================================================
echo UPDATE FAILED.
echo Nothing was pushed to GitHub.
echo ==============================================================
echo.
echo Take a screenshot of this window and send it to ChatGPT.
echo.
pause
exit /b 1

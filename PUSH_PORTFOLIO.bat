@echo off
setlocal EnableExtensions
cd /d "%~dp0"
title HM Portfolio - Push to GitHub

echo.
echo ==============================================================
echo   HM PORTFOLIO - PUSH TO GITHUB
echo ==============================================================
echo.

if not exist ".git" (
    echo ERROR: This does not look like the HM Portfolio Git folder.
    echo Put PUSH_PORTFOLIO.bat in the SAME main folder as index.html.
    echo.
    pause
    exit /b 1
)

if not exist "index.html" (
    echo ERROR: index.html was not found.
    echo Put PUSH_PORTFOLIO.bat in the main HM Portfolio folder.
    echo.
    pause
    exit /b 1
)

where git >nul 2>nul
if errorlevel 1 (
    echo ERROR: Git was not found on this computer.
    echo.
    pause
    exit /b 1
)

echo IMPORTANT:
echo Run UPDATE_PORTFOLIO.bat first and check index.html locally.
echo.
choice /C YN /N /M "Have you checked the local website and is everything correct? [Y/N]: "
if errorlevel 2 (
    echo.
    echo Push cancelled. Nothing was sent to GitHub.
    echo.
    pause
    exit /b 0
)

echo.
echo Checking for changes...
git status --short

git diff --quiet
set "WORKTREE_CLEAN=%ERRORLEVEL%"
git diff --cached --quiet
set "INDEX_CLEAN=%ERRORLEVEL%"

if "%WORKTREE_CLEAN%"=="0" if "%INDEX_CLEAN%"=="0" (
    echo.
    echo There are no new changes to push.
    echo.
    pause
    exit /b 0
)

echo.
echo [1/3] Adding all changes...
git add -A
if errorlevel 1 goto :failed

echo.
echo [2/3] Creating commit...
git diff --cached --quiet
if not errorlevel 1 (
    echo There are no staged changes to commit.
    goto :push_only
)

git commit -m "Update portfolio images"
if errorlevel 1 goto :failed

:push_only
echo.
echo [3/3] Pushing to GitHub...
git push origin main
if errorlevel 1 goto :failed

echo.
echo ==============================================================
echo PUSH COMPLETE.
echo ==============================================================
echo.
echo Your changes were sent to GitHub successfully.
echo Open the live website and refresh it to verify the update.
echo.
pause
exit /b 0

:failed
echo.
echo ==============================================================
echo PUSH FAILED.
echo ==============================================================
echo.
echo Git stopped because something went wrong.
echo Nothing else will be changed automatically.
echo Take a screenshot of this window and send it to ChatGPT.
echo.
pause
exit /b 1

@echo off
setlocal
title HM Knowledge Exact Practice V2
cd /d "%~dp0"

echo HM Knowledge Exact Practice V2
echo ------------------------------
echo.

if not exist "apply_knowledge_exact_practice_v2.py" (
  echo ERROR: apply_knowledge_exact_practice_v2.py is missing.
  pause
  exit /b 1
)

if not exist "index.html" (
  echo ERROR: index.html is not in this folder.
  echo Put both patch files directly inside your portfolio root folder.
  pause
  exit /b 1
)

py "apply_knowledge_exact_practice_v2.py"
echo.
pause

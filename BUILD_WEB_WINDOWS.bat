@echo off
setlocal enabledelayedexpansion
cd /d "%~dp0"

set GODOT=
for %%G in (godot4.exe godot.exe Godot_v4.7.2-stable_win64.exe) do (
  where %%G >nul 2>nul && set GODOT=%%G
)
if not defined GODOT (
  echo [ERROR] Godot executable was not found in PATH.
  echo Open this project in Godot 4.7.2 and export preset "Web" if needed.
  exit /b 1
)

echo [1/3] Importing project resources...
%GODOT% --headless --editor --path . --quit-after 2 || exit /b 1

echo [2/3] Running regression...
%GODOT% --headless --path . -- --shinobi-regression > web_regression.log 2>&1
findstr /C:"SHINOBI_REGRESSION PASS ALL:" web_regression.log >nul || (
  type web_regression.log
  echo [ERROR] Regression PASS marker not found.
  exit /b 1
)
findstr /C:"ERROR:" web_regression.log >nul && (
  type web_regression.log
  echo [ERROR] Godot reported an ERROR line.
  exit /b 1
)

echo [3/3] Exporting Web release...
if not exist web mkdir web
%GODOT% --headless --path . --export-release "Web" "web/index.html" || exit /b 1

echo [PASS] Web release generated in .\web\
endlocal
